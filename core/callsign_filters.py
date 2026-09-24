"""Shared SQL population filters for remote WSPR peer identities."""

from config.app_config import SPECIAL_CALLSIGN_PREFIXES


def build_peer_callsign_exclusion_sql(
    *, mode: str, exclude_special_callsigns: bool,
) -> str:
    """Return leading AND predicates for remote peers, or empty text if disabled.

    Canonical RX analyses filter transmitting peers; TX analyses filter receiving
    peers. Target, fixed Reference and Local Neighborhood reference contributors
    are on the other endpoint and remain eligible. Only the fixed endpoint
    columns are selected; an unsupported direction raises ValueError.
    """
    if mode == "RX":
        peer_sign_column = "tx_sign"
    elif mode == "TX":
        peer_sign_column = "rx_sign"
    else:
        raise ValueError("mode must be RX or TX.")

    if not exclude_special_callsigns:
        return ""
    return "".join(
        f" AND {peer_sign_column} NOT LIKE '{prefix}%'"
        for prefix in SPECIAL_CALLSIGN_PREFIXES
    )
