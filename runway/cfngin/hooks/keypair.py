"""AWS EC2 keypair hook."""
from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

from botocore.exceptions import ClientError
from typing_extensions import Literal, TypedDict

from ..ui import get_raw_input

if TYPE_CHECKING:
    from mypy_boto3_ec2.client import EC2Client
    from mypy_boto3_ec2.type_defs import ImportKeyPairResultTypeDef, KeyPairTypeDef
    from mypy_boto3_ssm.client import SSMClient

    from ...context import CfnginContext

LOGGER = logging.getLogger(__name__)

KEYPAIR_LOG_MESSAGE = "keypair %s (%s) %s"


class KeyPairInfo(TypedDict, total=False):
    """Value returned from get_existing_key_pair."""

    file_path: Path
    fingerprint: str
    key_name: str
    status: Literal["created", "exists", "imported"]


def get_existing_key_pair(ec2: EC2Client, keypair_name: str) -> Optional[KeyPairInfo]:
    """Get existing keypair."""
    resp = ec2.describe_key_pairs()
    keypair = next(
        (kp for kp in resp.get("KeyPairs", {}) if kp.get("KeyName") == keypair_name),
        None,
    )

    if keypair:
        LOGGER.info(
            KEYPAIR_LOG_MESSAGE,
            keypair.get("KeyName"),
            keypair.get("KeyFingerprint"),
            "exists",
        )
        return {
            "status": "exists",
            "key_name": keypair.get("KeyName", ""),
            "fingerprint": keypair.get("KeyFingerprint", ""),
        }

    LOGGER.info('keypair "%s" not found', keypair_name)
    return None


def import_key_pair(
    ec2: EC2Client, keypair_name: str, public_key_data: bytes
) -> ImportKeyPairResultTypeDef:
    """Import keypair."""
    keypair = ec2.import_key_pair(
        KeyName=keypair_name, PublicKeyMaterial=public_key_data.strip(), DryRun=False
    )
    LOGGER.info(
        KEYPAIR_LOG_MESSAGE,
        keypair.get("KeyName"),
        keypair.get("KeyFingerprint"),
        "imported",
    )
    return keypair


def read_public_key_file(path: Path) -> Optional[bytes]:
    """Read public key file."""
    try:
        data = path.read_bytes()
        if not data.startswith(b"ssh-rsa"):
            raise ValueError(
                "Bad public key data, must be an RSA key in SSH authorized "
                "keys format (beginning with `ssh-rsa`)"
            )
        return data.strip()
    except (ValueError, OSError) as err:
        LOGGER.error('failed to read public key file :%s": %s', path, str(err))
        return None


def create_key_pair_from_public_key_file(
    ec2: EC2Client, keypair_name: str, public_key_path: Path
) -> Optional[KeyPairInfo]:
    """Create keypair from public key file."""
    public_key_data = read_public_key_file(public_key_path)
    if not public_key_data:
        return None

    keypair = import_key_pair(ec2, keypair_name, public_key_data)
    return {
        "status": "imported",
        "key_name": keypair.get("KeyName", ""),
        "fingerprint": keypair.get("KeyFingerprint", ""),
    }


def create_key_pair_in_ssm(
    ec2: EC2Client,
    ssm: SSMClient,
    keypair_name: str,
    parameter_name: str,
    kms_key_id: Optional[str] = None,
) -> Optional[KeyPairInfo]:
    """Create keypair in SSM."""
    keypair = create_key_pair(ec2, keypair_name)
    try:
        kms_key_label = "default"
        kms_args: Dict[str, Any] = {}
        if kms_key_id:
            kms_key_label = kms_key_id
            kms_args = {"KeyId": kms_key_id}

        LOGGER.info(
            'storing generated key in SSM parameter "%s" using KMS key "%s"',
            parameter_name,
            kms_key_label,
        )

        ssm.put_parameter(
            Name=parameter_name,
            Description=f'SSH private key for KeyPair "{keypair_name}" (generated by Runway)',
            Value=keypair["KeyMaterial"],
            Type="SecureString",
            Overwrite=False,
            **kms_args,
        )
    except ClientError:
        # Erase the key pair if we failed to store it in SSM, since the
        # private key will be lost anyway

        LOGGER.exception(
            "failed to store generated key in SSM; deleting "
            "created key pair as private key will be lost"
        )
        ec2.delete_key_pair(KeyName=keypair_name, DryRun=False)
        return None

    return {
        "status": "created",
        "key_name": keypair.get("KeyName", ""),
        "fingerprint": keypair.get("KeyFingerprint", ""),
    }


def create_key_pair(ec2: EC2Client, keypair_name: str) -> KeyPairTypeDef:
    """Create keypair."""
    keypair = ec2.create_key_pair(KeyName=keypair_name, DryRun=False)
    LOGGER.info(
        KEYPAIR_LOG_MESSAGE,
        keypair.get("KeyName"),
        keypair.get("KeyFingerprint"),
        "created",
    )
    return keypair


def create_key_pair_local(
    ec2: EC2Client, keypair_name: str, dest_dir: Path
) -> Optional[KeyPairInfo]:
    """Create local keypair."""
    dest_dir = dest_dir.resolve()
    if not dest_dir.is_dir():
        LOGGER.error('"%s" is not a valid directory', dest_dir)
        return None

    key_path = dest_dir / f"{keypair_name}.pem"
    if key_path.is_file():
        # This mimics the old boto2 keypair.save error
        LOGGER.error('"%s" already exists in directory "%s"', key_path.name, dest_dir)
        return None

    keypair = create_key_pair(ec2, keypair_name)
    key_path.write_text(keypair.get("KeyMaterial", ""), encoding="ascii")

    return {
        "status": "created",
        "key_name": keypair.get("KeyName", ""),
        "fingerprint": keypair.get("KeyFingerprint", ""),
        "file_path": key_path,
    }


def interactive_prompt(
    keypair_name: str,
) -> Tuple[Optional[Literal["create", "import"]], Optional[str]]:
    """Interactive prompt."""
    if not sys.stdin.isatty():
        return None, None

    try:
        while True:
            action = get_raw_input(
                'import or create keypair "%s"? (import/create/cancel) '
                % (keypair_name,)
            )

            if action.lower() == "cancel":
                break

            if action.lower() in ("i", "import"):
                path = get_raw_input("path to keypair file: ")
                return "import", path.strip()

            if action.lower() == "create":
                path = get_raw_input("directory to save keyfile: ")
                return "create", path.strip()
    except (EOFError, KeyboardInterrupt):
        return None, None

    return None, None


def ensure_keypair_exists(
    context: CfnginContext,
    *,
    keypair: str,
    public_key_path: Optional[str] = None,
    ssm_key_id: Optional[str] = None,
    ssm_parameter_name: Optional[str] = None,
    **_: Any,
) -> KeyPairInfo:
    """Ensure a specific keypair exists within AWS.

    If the key doesn't exist, upload it.

    Args:
        context: Context instance. (passed in by CFNgin)
        keypair: Name of the key pair to create
        public_key_path: Path to a public key file to be imported instead of
            generating a new key. Incompatible with the SSM options, as the
            private key will not be available for storing.
        ssm_key_id: ID of a KMS key to encrypt the SSM parameter with.
            If omitted, the default key will be used.
        ssm_parameter_name: Path to an SSM store parameter to receive the
            generated private key, instead of importing it or storing it locally.

    """
    if public_key_path and ssm_parameter_name:
        LOGGER.error(
            "public_key_path and ssm_parameter_name cannot be "
            "specified at the same time"
        )
        return {}

    session = context.get_session()
    ec2 = session.client("ec2")

    keypair_info = get_existing_key_pair(ec2, keypair)
    if keypair_info:
        return keypair_info

    if public_key_path:
        keypair_info = create_key_pair_from_public_key_file(
            ec2, keypair, Path(public_key_path)
        )
    elif ssm_parameter_name:
        ssm = session.client("ssm")
        keypair_info = create_key_pair_in_ssm(
            ec2, ssm, keypair, ssm_parameter_name, ssm_key_id
        )
    else:
        action, path = interactive_prompt(keypair)
        if action == "import" and path:
            keypair_info = create_key_pair_from_public_key_file(
                ec2, keypair, Path(path)
            )
        elif action == "create" and path:
            keypair_info = create_key_pair_local(ec2, keypair, Path(path))
        else:
            LOGGER.error("no action to find keypair or path not provided")

    if not keypair_info:
        return {}

    return keypair_info
