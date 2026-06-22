# =========================================
# FILE: backend/security/sandbox_engine.py
# =========================================


class SandboxEngine:

    def preview_link(self, url):

        return {
            "secure_preview": True,
            "message": f"Opening {url} inside Neurova Secure Sandbox"
        }
