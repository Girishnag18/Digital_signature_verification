import json
from typing import Iterator, Dict, Optional, List


def _yield(step: str, message: str, data: Optional[Dict] = None) -> Dict:
    """Helper to standardize stream messages."""
    payload = {"type": step, "message": message}
    if data is not None:
        payload["data"] = data
    return payload


def verify_pdf_signature_stream(
    pdf_path: str,
    trust_roots_pem: Optional[List[str]] = None,
) -> Iterator[Dict]:
    """
    Stream verification progress for a PDF's digital signature(s).

    Yields dictionaries with fields: {type, message, data?} to be serialized as SSE/streaming JSON.

    - type: status|warning|error|result|done
    - message: text to display
    - data: optional structured info

    Uses pyHanko if available for real cryptographic verification.
    If pyHanko is not installed, emits an error instructing to install it.
    """
    # Step 1: Try import dependencies lazily so app can still start without them
    yield _yield("status", "Initializing verifier...")

    try:
        from pyhanko.pdf_utils.reader import PdfFileReader
        from pyhanko.sign.validation import validate_pdf_signature
        from pyhanko_certvalidator import ValidationContext
        from cryptography import x509  # for typing and potential parsing
    except Exception as e:
        yield _yield(
            "error",
            "Real signature verification library (pyHanko) not available. Please install dependencies.",
            {"details": str(e)},
        )
        yield _yield("done", "Stopped due to missing dependencies.")
        return

    # Step 2: Prepare validation context
    try:
        yield _yield("status", "Preparing validation context...")
        trust_certs = []
        if trust_roots_pem:
            import os
            from cryptography.hazmat.primitives import serialization

            for pem_path in trust_roots_pem:
                if pem_path and os.path.exists(pem_path):
                    try:
                        with open(pem_path, "rb") as f:
                            # Load one or more PEM certs from file
                            pem_data = f.read()
                        # pyHanko-certvalidator accepts trust_roots as cryptography.x509.Certificate objects
                        from cryptography.hazmat.backends import default_backend
                        while pem_data:
                            try:
                                cert = x509.load_pem_x509_certificate(pem_data, default_backend())
                                trust_certs.append(cert)
                                # Trim consumed cert — simple split by footer
                                end_marker = b"-----END CERTIFICATE-----"
                                idx = pem_data.find(end_marker)
                                if idx == -1:
                                    break
                                pem_data = pem_data[idx + len(end_marker):].strip()
                            except Exception:
                                break
                    except Exception:
                        # If trust root loading fails, continue without that file
                        pass
        vc = ValidationContext(trust_roots=trust_certs or None, allow_fetching=True)
    except Exception as e:
        yield _yield("warning", "Falling back to default validation context.", {"details": str(e)})
        vc = ValidationContext(allow_fetching=True)

    # Step 3: Open PDF and enumerate signatures
    yield _yield("status", "Opening PDF and locating signatures...")
    try:
        with open(pdf_path, "rb") as inf:
            reader = PdfFileReader(inf)
            signatures = list(reader.embedded_signatures)
            if not signatures:
                yield _yield("error", "No embedded digital signatures found in the PDF.")
                yield _yield("done", "Verification completed.")
                return

            yield _yield(
                "status",
                f"Found {len(signatures)} signature(s). Starting validation...",
            )

            overall_ok = True
            results = []

            for idx, sig in enumerate(signatures, start=1):
                yield _yield("status", f"Validating signature {idx} of {len(signatures)}...")
                try:
                    status = validate_pdf_signature(sig, vc)

                    # Make a best-effort to extract booleans; pyHanko's API can vary by version
                    trusted = getattr(status, "trusted", None)
                    valid = getattr(status, "valid", None)

                    # Try to fetch a human-readable summary if available
                    detail_text = None
                    for attr in ("pretty_print_details", "summary", "__str__"):
                        if hasattr(status, attr):
                            try:
                                detail_text = getattr(status, attr)()
                                if isinstance(detail_text, str):
                                    break
                            except Exception:
                                continue
                    if not isinstance(detail_text, str):
                        detail_text = str(status)

                    # Decide a conservative verdict
                    sig_ok = bool(valid) if valid is not None else (bool(trusted) if trusted is not None else False)
                    overall_ok = overall_ok and sig_ok

                    results.append({
                        "index": idx,
                        "trusted": trusted,
                        "valid": valid,
                        "details": detail_text,
                    })

                    yield _yield(
                        "status",
                        f"Signature {idx}: {'OK' if sig_ok else 'NOT OK'}",
                        {"trusted": trusted, "valid": valid},
                    )
                except Exception as e:
                    overall_ok = False
                    results.append({
                        "index": idx,
                        "trusted": False,
                        "valid": False,
                        "details": f"Validation error: {e}",
                    })
                    yield _yield("error", f"Signature {idx} validation failed.", {"details": str(e)})

            # Final result
            yield _yield(
                "result",
                "All signatures validated." if overall_ok else "One or more signatures failed validation.",
                {"ok": overall_ok, "signatures": results},
            )
            yield _yield("done", "Verification completed.")
    except Exception as e:
        yield _yield("error", "Failed to process PDF.", {"details": str(e)})
        yield _yield("done", "Verification terminated with errors.")


# Keep the old API for compatibility (non-streaming), but switch to real verification if possible

def verify_pdf_signature(pdf_path: str, public_key_path: Optional[str] = None):
    """
    Backwards-compatible, non-streaming checker. Returns (bool, message).
    Internally uses the streaming verifier and aggregates the result.
    """
    overall_ok = False
    details = []
    for evt in verify_pdf_signature_stream(pdf_path):
        if evt.get("type") == "result":
            overall_ok = bool(evt.get("data", {}).get("ok", False))
            details.append(evt.get("message", ""))
        elif evt.get("type") == "error":
            details.append(evt.get("message", ""))
    return overall_ok, "; ".join([d for d in details if d]) or ("Valid signature." if overall_ok else "Signature verification failed.")