# -*- coding: utf-8 -*-
"""IOT Solar AutoTest HTTP 客户端（出站 HTTPS/HTTP）。"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, Optional


class IotSolarClient:
    def __init__(self, base: str, token: str, timeout: float = 30.0):
        self.base = base.rstrip("/")
        self.token = token
        self.timeout = timeout

    def _request(self, method: str, path: str, body: Optional[dict] = None) -> Dict[str, Any]:
        url = f"{self.base}{path}"
        data = None
        headers = {
            "X-Solar-Agent-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if body is not None:
            data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} {path}: {detail}") from e

    def heartbeat(
        self,
        *,
        agent_version: str = "",
        host_name: str = "",
        busy: bool = False,
        fault: bool = False,
    ) -> Dict[str, Any]:
        return self._request(
            "POST",
            "/api/solar-autotest/agent/heartbeat",
            {
                "agentVersion": agent_version,
                "hostName": host_name,
                "busy": busy,
                "fault": fault,
            },
        )

    def claim_next(self) -> Optional[Dict[str, Any]]:
        res = self._request("GET", "/api/solar-autotest/agent/jobs/next")
        return res.get("data")

    def progress(
        self,
        job_id: int,
        *,
        progress_percent: Optional[int] = None,
        progress_text: str = "",
        current_step: str = "",
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "progressText": progress_text,
            "currentStep": current_step,
        }
        if progress_percent is not None:
            body["progressPercent"] = progress_percent
        return self._request("POST", f"/api/solar-autotest/agent/jobs/{job_id}/progress", body)

    def done(
        self,
        job_id: int,
        *,
        status: str,
        fail_reason: str = "",
        result_summary: Optional[dict] = None,
        report_meta: Optional[list] = None,
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "status": status,
            "failReason": fail_reason,
            "resultSummary": result_summary or {},
        }
        if report_meta:
            body["reportMeta"] = report_meta
        return self._request(
            "POST",
            f"/api/solar-autotest/agent/jobs/{job_id}/done",
            body,
        )

    def reject(self, job_id: int, reason: str) -> Dict[str, Any]:
        return self._request(
            "POST",
            f"/api/solar-autotest/agent/jobs/{job_id}/reject",
            {"reason": reason},
        )

    def upload_report(self, job_id: int, file_path: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """multipart 上传报告文件到 IOT。"""
        import mimetypes
        from pathlib import Path

        path = Path(file_path)
        name = filename or path.name
        boundary = "----SolarAgentBoundary7MA4YWxk"
        raw = path.read_bytes()
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="file"; filename="{name}"\r\n'
            f"Content-Type: {ctype}\r\n\r\n"
        ).encode("utf-8") + raw + f"\r\n--{boundary}--\r\n".encode("utf-8")
        url = f"{self.base}/api/solar-autotest/agent/jobs/{job_id}/report"
        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "X-Solar-Agent-Token": self.token,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8") or "{}")
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"HTTP {e.code} upload_report: {detail}") from e
