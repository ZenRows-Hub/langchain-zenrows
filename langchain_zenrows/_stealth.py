"""Adaptive Stealth Mode resolution shared by the Fetch and Extract tools."""

from typing import Any, Dict, Iterable

# Adaptive Stealth Mode ignores these, so a page that needs them comes back empty.
WAIT_PARAMS = ("wait", "wait_for")


def apply_stealth(
    params: Dict[str, Any],
    *,
    adaptive_stealth: bool,
    js_required_params: Iterable[str],
) -> None:
    """Decide between Adaptive Stealth Mode and manual flags, in place.

    Zenrows rejects ``mode=auto`` together with ``js_render`` or
    ``premium_proxy`` (REQS004), so a request carries one or the other:

    * ``js_render`` / ``premium_proxy`` set by the caller pick the tier
      themselves, so Adaptive Stealth Mode is dropped.
    * A browser-only option (``wait_for``, a screenshot, ...) needs a browser
      that Adaptive Stealth Mode doesn't guarantee, so it switches to
      ``js_render`` as the tools always have.
    * Otherwise, with ``adaptive_stealth`` on, ``mode=auto`` is sent. It
      geolocates on its own, so ``proxy_country`` goes alone.
    * Outside Adaptive Stealth Mode the API only accepts ``proxy_country``
      together with ``premium_proxy``, so it's enabled.

    An explicit ``mode="auto"`` from the caller is honoured as asked: it can't
    be combined with ``js_render`` / ``premium_proxy``, nor with ``wait`` /
    ``wait_for``, which Adaptive Stealth Mode ignores. Other browser-only
    options don't switch it off.
    """
    explicit_mode = params.get("mode") == "auto"
    explicit_flags = bool(params.get("js_render") or params.get("premium_proxy"))

    if explicit_mode:
        if explicit_flags:
            raise ValueError(
                "mode='auto' (Adaptive Stealth Mode) can't be combined with "
                "js_render or premium_proxy; Zenrows rejects them together. "
                "Drop mode to set those yourself, or drop them to keep "
                "Adaptive Stealth Mode."
            )
        waits = [p for p in WAIT_PARAMS if params.get(p)]
        if waits:
            raise ValueError(
                f"mode='auto' (Adaptive Stealth Mode) ignores {' and '.join(waits)}, "
                "so the page may come back before it has loaded. Drop mode to "
                "wait with js_render, or drop the wait."
            )
        return

    needs_browser = any(params.get(p) for p in js_required_params)
    if adaptive_stealth and not explicit_flags and not needs_browser:
        params["mode"] = "auto"
        return

    params.pop("mode", None)
    if needs_browser:
        params["js_render"] = True
    if params.get("proxy_country"):
        params["premium_proxy"] = True
