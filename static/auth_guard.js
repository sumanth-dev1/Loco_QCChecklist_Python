(function (global) {
  const AUTH_STORAGE_KEYS = ["user_id", "username", "employee_name", "role"];

  /**
   * Clear authentication-related keys from localStorage.
   */
  function clearAuthStorage() {
    AUTH_STORAGE_KEYS.forEach(function (key) {
      localStorage.removeItem(key);
    });
  }

  /**
   * Capture current auth keys before resetting checklist storage.
   */
  function snapshotAuthStorage() {
    const snapshot = {};
    AUTH_STORAGE_KEYS.forEach(function (key) {
      const value = localStorage.getItem(key);
      if (value !== null) {
        snapshot[key] = value;
      }
    });
    return snapshot;
  }

  /**
   * Restore previously captured auth keys to localStorage.
   */
  function restoreAuthStorage(snapshot) {
    Object.keys(snapshot || {}).forEach(function (key) {
      localStorage.setItem(key, snapshot[key]);
    });
  }

  /**
   * Synchronize localStorage auth metadata from the server session payload.
   */
  function syncAuthStorage(data) {
    if (data.user_id) {
      localStorage.setItem("user_id", data.user_id);
    }
    if (data.username) {
      localStorage.setItem("username", data.username);
    }
    if (data.employee_name !== undefined && data.employee_name !== null) {
      localStorage.setItem("employee_name", data.employee_name);
    }
    if (data.role) {
      localStorage.setItem("role", data.role);
    } else {
      localStorage.removeItem("role");
    }
  }

  /**
   * Verify server-side session status (catches bfcache Back navigation after logout).
   */
  async function ensureAuthenticated() {
    try {
      const res = await fetch("auth-status", {
        cache: "no-store",
        credentials: "same-origin"
      });
      if (!res.ok) return;
      const data = await res.json();
      if (!data.authenticated) {
        clearAuthStorage();
        if (typeof global.beforeUnloadHandler === "function") {
          global.removeEventListener("beforeunload", global.beforeUnloadHandler);
        }
        global.location.replace("login.html");
        return;
      }
      syncAuthStorage(data);
    } catch (err) {
      console.error("Auth status check failed:", err);
    }
  }

  /**
   * Navigate to /logout to end the server session (storage is cleared once
   * navigation commits to login.html, so cancelling beforeunload keeps drafts).
   */
  function performLogout(showAlert) {
    if (showAlert) {
      alert("Logging out...");
    }
    global.location.href = "logout";
  }

  global.AuthGuard = {
    clearAuthStorage: clearAuthStorage,
    snapshotAuthStorage: snapshotAuthStorage,
    restoreAuthStorage: restoreAuthStorage,
    syncAuthStorage: syncAuthStorage,
    ensureAuthenticated: ensureAuthenticated,
    performLogout: performLogout
  };

  if (document.currentScript && document.currentScript.getAttribute("data-require-auth") === "true") {
    global.addEventListener("pageshow", function () {
      ensureAuthenticated();
    });
  }
})(window);
