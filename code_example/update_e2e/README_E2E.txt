# -*- coding: utf-8 -*-
"""Record of local HTTP auto-update E2E (no GitLab token required for this path)."""
print(
    """
E2E result (2026-09-05):
- Channel: local HTTP http://127.0.0.1:18765/
- Flow: Check-And-Update -> download latest.json + zip -> Install -> VERSION upgraded
- Status: E2E_HTTP_UPDATE_OK

GitLab real publish still needs ONE Deploy Token on the build PC
(or CI Job Token via windows runner). Bench PCs: public package pull, no token.
"""
)
