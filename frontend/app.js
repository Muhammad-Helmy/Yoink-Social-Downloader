/**
 * Yoink Social — Frontend Controller
 * Liquid Glass & VisionOS Architecture with Universal Queue & Synthetic Water Droplet SFX
 * Made by Heru
 */

// ============================================================================
// Web Audio API — Liquid Glass Water Droplet SFX Synthesizer
// ============================================================================
const GlassAudio = {
  ctx: null,

  init() {
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === "suspended") {
      this.ctx.resume();
    }
  },

  playDrop() {
    try {
      this.init();
      if (!this.ctx) return;

      const now = this.ctx.currentTime;

      // Master gain envelope for water droplet
      const masterGain = this.ctx.createGain();
      masterGain.gain.setValueAtTime(0.28, now);
      masterGain.gain.exponentialRampToValueAtTime(0.0008, now + 0.13);
      masterGain.connect(this.ctx.destination);

      // Primary sine droplet pitch upward sweep (mimics droplet surface-tension ping)
      const osc = this.ctx.createOscillator();
      osc.type = "sine";
      osc.frequency.setValueAtTime(560, now);
      osc.frequency.exponentialRampToValueAtTime(1850, now + 0.038);
      osc.frequency.exponentialRampToValueAtTime(1150, now + 0.09);

      // Liquid bandpass filter
      const filter = this.ctx.createBiquadFilter();
      filter.type = "bandpass";
      filter.frequency.setValueAtTime(1450, now);
      filter.Q.setValueAtTime(11, now);

      osc.connect(filter);
      filter.connect(masterGain);

      // Glass body resonance bubble pop
      const subOsc = this.ctx.createOscillator();
      const subGain = this.ctx.createGain();
      subOsc.type = "sine";
      subOsc.frequency.setValueAtTime(260, now);
      subOsc.frequency.exponentialRampToValueAtTime(130, now + 0.045);
      subGain.gain.setValueAtTime(0.16, now);
      subGain.gain.exponentialRampToValueAtTime(0.001, now + 0.045);
      subOsc.connect(subGain);
      subGain.connect(this.ctx.destination);

      osc.start(now);
      osc.stop(now + 0.13);
      subOsc.start(now);
      subOsc.stop(now + 0.045);
    } catch (e) {
      // Harmless audio autoplay policy catch
    }
  }
};

// Global click event delegation for Liquid Water Drop SFX
document.addEventListener("click", (e) => {
  const trigger = e.target.closest("button, .nav-tab, .seg-btn, .dropdown-item, .dropdown-trigger, .lang-option, .lang-pill, .btn-icon, .header-task-capsule");
  if (trigger) {
    GlassAudio.playDrop();
  }
});

// ============================================================================
// Main Application Controller
// ============================================================================
const app = {
  platforms: ["youtube", "tiktok", "instagram", "facebook"],
  platform: "youtube",
  currentView: "youtube",
  activeTask: null,
  queueTasks: [],
  logEntries: [],
  hardwareInfo: null,
  downloadedFilePath: null,

  // Dedicated Per-Platform State Storage
  platformStates: {
    youtube: { url: "", metadata: null, format: "video", quality: "best" },
    tiktok: { url: "", metadata: null, format: "video", quality: "best" },
    instagram: { url: "", metadata: null, format: "video", quality: "best" },
    facebook: { url: "", metadata: null, format: "video", quality: "best" }
  },

  init() {
    this.bindEvents();
    this.applyTranslations();
    this.updatePlatformUI();

    // Check pywebview API readiness
    window.addEventListener("pywebviewready", () => {
      console.log("pywebview API ready");
      this.loadSettings();
      this.loadHistory();
      this.refreshQueue();
    });

    if (window.pywebview && window.pywebview.api) {
      this.loadSettings();
      this.loadHistory();
      this.refreshQueue();
    }
  },

  async getApi() {
    const isApiValid = (api) => api && (typeof api.fetch_info === "function" || typeof api.get_settings === "function");
    if (window.pywebview && isApiValid(window.pywebview.api)) {
      return window.pywebview.api;
    }
    for (let i = 0; i < 50; i++) {
      await new Promise(r => setTimeout(r, 100));
      if (window.pywebview && isApiValid(window.pywebview.api)) {
        return window.pywebview.api;
      }
    }
    return (window.pywebview && window.pywebview.api) || null;
  },

  applyTranslations() {
    const lang = I18N.currentLang;
    
    // Update all elements with data-i18n
    document.querySelectorAll("[data-i18n]").forEach(el => {
      const key = el.dataset.i18n;
      const text = I18N.t(key);
      if (text) {
        if (el.tagName === "INPUT") {
          el.placeholder = text;
        } else {
          el.textContent = text;
        }
      }
    });

    // Update Language Button in Header
    const flagMap = { en: "🇬🇧", id: "🇮🇩", es: "🇪🇸" };
    const codeMap = { en: "EN", id: "ID", es: "ES" };
    const flagEl = document.getElementById("current-lang-flag");
    const codeEl = document.getElementById("current-lang-code");
    if (flagEl) flagEl.textContent = flagMap[lang] || "🇬🇧";
    if (codeEl) codeEl.textContent = codeMap[lang] || "EN";

    // Update active state in dropdown and settings pills
    document.querySelectorAll(".lang-option").forEach(opt => {
      opt.classList.toggle("active", opt.dataset.lang === lang);
    });
    document.querySelectorAll(".lang-pill").forEach(pill => {
      pill.classList.toggle("active", pill.dataset.setLang === lang);
    });

    this.updatePlatformUI();
  },

  setLanguage(lang) {
    I18N.setLanguage(lang);
    this.applyTranslations();

    // Save language to backend config
    this.getApi().then(api => {
      if (api) {
        api.get_settings().then(cfg => {
          if (cfg) {
            cfg.language = lang;
            api.save_settings(cfg);
          }
        });
      }
    });
  },

  bindEvents() {
    // Platform Navigation Tabs
    document.querySelectorAll(".nav-tab[data-platform]").forEach(tab => {
      tab.addEventListener("click", () => {
        const plat = tab.dataset.platform;
        if (plat) {
          this.switchPlatform(plat);
        }
      });
    });

    // System Navigation Tabs (Active Tasks, History, Settings, About)
    document.querySelectorAll(".nav-tab[data-view]").forEach(tab => {
      tab.addEventListener("click", () => {
        const view = tab.dataset.view;
        if (view) {
          this.switchView(view);
        }
      });
    });

    // Header active task capsule
    const headerCapsule = document.getElementById("header-task-capsule");
    if (headerCapsule) {
      headerCapsule.addEventListener("click", () => {
        this.switchView("downloads");
      });
    }

    // Bind Per-Platform Inputs and Buttons
    this.platforms.forEach(plat => {
      const inputUrl = document.getElementById(`input-url-${plat}`);
      const btnPaste = document.getElementById(`btn-paste-url-${plat}`);
      const btnClear = document.getElementById(`btn-clear-url-${plat}`);
      const btnAnalyze = document.getElementById(`btn-analyze-${plat}`);
      const btnDownload = document.getElementById(`btn-start-download-${plat}`);
      const btnQualityTrigger = document.getElementById(`btn-quality-trigger-${plat}`);

      if (inputUrl) {
        inputUrl.addEventListener("input", () => {
          const val = inputUrl.value.trim();
          this.platformStates[plat].url = val;
          if (btnClear) {
            btnClear.classList.toggle("hidden", val.length === 0);
          }
          this.detectPlatformFromUrl(val);
        });

        inputUrl.addEventListener("keydown", (e) => {
          if (e.key === "Enter") {
            this.fetchInfo(plat);
          }
        });
      }

      if (btnPaste && inputUrl) {
        btnPaste.addEventListener("click", async () => {
          try {
            const text = await navigator.clipboard.readText();
            if (text) {
              inputUrl.value = text.trim();
              this.platformStates[plat].url = text.trim();
              if (btnClear) btnClear.classList.remove("hidden");
              this.detectPlatformFromUrl(text.trim());
              this.fetchInfo(plat);
            }
          } catch (err) {
            this.addLog("warning", "Please grant clipboard access or use Ctrl+V.");
          }
        });
      }

      if (btnClear && inputUrl) {
        btnClear.addEventListener("click", () => {
          inputUrl.value = "";
          this.platformStates[plat].url = "";
          btnClear.classList.add("hidden");
          this.resetPreview(plat);
        });
      }

      if (btnAnalyze) {
        btnAnalyze.addEventListener("click", () => {
          this.fetchInfo(plat);
        });
      }

      if (btnDownload) {
        btnDownload.addEventListener("click", () => {
          this.startDownload(plat);
        });
      }

      if (btnQualityTrigger) {
        btnQualityTrigger.addEventListener("click", (e) => {
          e.stopPropagation();
          this.toggleQualityDropdown(plat);
        });
      }

      // Segmented Format buttons for this platform
      ["video", "audio", "image"].forEach(fmt => {
        const btnFmt = document.getElementById(`btn-format-${fmt}-${plat}`);
        if (btnFmt) {
          btnFmt.addEventListener("click", () => {
            this.setFormat(plat, fmt);
          });
        }
      });

      // Finish Card actions for this platform
      const btnFinishOpenFile = document.getElementById(`btn-finish-open-file-${plat}`);
      if (btnFinishOpenFile) {
        btnFinishOpenFile.addEventListener("click", () => {
          const targetPath = (this.platformStates[plat] && this.platformStates[plat].downloadedFilePath) || this.downloadedFilePath;
          if (targetPath) {
            this.getApi().then(api => {
              if (api) {
                api.open_file(targetPath).then(res => {
                  if (res && !res.success) {
                    this.addLog("error", `❌ ${res.error || "Cannot open file."}`);
                  }
                });
              }
            });
          } else {
            this.openFolder(plat);
          }
        });
      }

      const btnFinishOpenFolder = document.getElementById(`btn-finish-open-folder-${plat}`);
      if (btnFinishOpenFolder) {
        btnFinishOpenFolder.addEventListener("click", () => {
          this.openFolder(plat);
        });
      }
    });

    // Close any custom dropdown when clicking outside
    document.addEventListener("click", () => {
      const langDropdown = document.getElementById("lang-dropdown");
      if (langDropdown) langDropdown.classList.add("hidden");
      this.platforms.forEach(p => this.closeQualityDropdown(p));
    });

    // Language Dropdown in Header
    const btnLangToggle = document.getElementById("btn-lang-toggle");
    const langDropdown = document.getElementById("lang-dropdown");
    if (btnLangToggle && langDropdown) {
      btnLangToggle.addEventListener("click", (e) => {
        e.stopPropagation();
        langDropdown.classList.toggle("hidden");
      });
    }

    document.querySelectorAll(".lang-option").forEach(opt => {
      opt.addEventListener("click", () => {
        const lang = opt.dataset.lang;
        this.setLanguage(lang);
        if (langDropdown) langDropdown.classList.add("hidden");
      });
    });

    document.querySelectorAll(".lang-pill").forEach(pill => {
      pill.addEventListener("click", () => {
        const lang = pill.dataset.setLang;
        this.setLanguage(lang);
      });
    });

    // Header Open Active Folder
    const btnOpenActiveFolder = document.getElementById("btn-open-active-folder");
    if (btnOpenActiveFolder) {
      btnOpenActiveFolder.addEventListener("click", () => {
        this.openFolder(this.platform);
      });
    }

    // Cancel Active Task button in Active Tasks view
    const btnCancelActiveTask = document.getElementById("btn-cancel-active-task");
    if (btnCancelActiveTask) {
      btnCancelActiveTask.addEventListener("click", () => {
        this.cancelDownload();
      });
    }

    // Clear History Button
    const btnClearHistory = document.getElementById("btn-clear-history-list");
    if (btnClearHistory) {
      btnClearHistory.addEventListener("click", async () => {
        const api = await this.getApi();
        if (api) {
          await api.clear_history();
          this.loadHistory();
        }
      });
    }

    // Hardware Acceleration Radio Options
    document.querySelectorAll("input[name='hardware_mode']").forEach(radio => {
      radio.addEventListener("change", (e) => {
        const mode = e.target.value;
        this.saveHardwareMode(mode);
      });
    });

    // Folder select buttons in Settings
    this.platforms.forEach(plat => {
      const btnChoose = document.getElementById(`btn-choose-folder-${plat}`);
      if (btnChoose) {
        btnChoose.addEventListener("click", () => this.chooseFolder(plat));
      }
      const btnOpen = document.getElementById(`btn-open-folder-${plat}`);
      if (btnOpen) {
        btnOpen.addEventListener("click", () => this.openFolder(plat));
      }
    });

    // Private Modal Close Button & Backdrop Dismiss
    const privateModal = document.getElementById("private-modal");
    const btnClosePrivateModal = document.getElementById("btn-close-private-modal");
    if (btnClosePrivateModal && privateModal) {
      btnClosePrivateModal.addEventListener("click", () => {
        privateModal.classList.add("hidden");
      });
      privateModal.addEventListener("click", (e) => {
        if (e.target === privateModal) {
          privateModal.classList.add("hidden");
        }
      });
    }

    // Log Controls & Toggle
    const btnCopyLog = document.getElementById("btn-copy-log");
    const btnClearLog = document.getElementById("btn-clear-log");
    const btnToggleLog = document.getElementById("btn-toggle-log");
    if (btnCopyLog) btnCopyLog.addEventListener("click", () => this.copyAllLogs());
    if (btnClearLog) btnClearLog.addEventListener("click", () => this.clearLogs());
    if (btnToggleLog) btnToggleLog.addEventListener("click", () => this.toggleLogSection());

    // Extractor Maintenance
    const btnCheckUpdate = document.getElementById("btn-check-update");
    const btnRunUpdate = document.getElementById("btn-run-update");
    if (btnCheckUpdate) btnCheckUpdate.addEventListener("click", () => this.checkUpdate());
    if (btnRunUpdate) btnRunUpdate.addEventListener("click", () => this.runUpdate());
  },

  toggleLogSection() {
    const logSection = document.querySelector(".log-section");
    if (logSection) {
      logSection.classList.toggle("collapsed");
    }
  },

  showPrivateModal(customMessage = null) {
    const modal = document.getElementById("private-modal");
    if (!modal) return;
    const bodyEl = modal.querySelector(".modal-body");
    const titleEl = modal.querySelector(".modal-title");
    if (titleEl) titleEl.textContent = I18N.t("private_modal_title") || "🔒 Private Content Notice";
    if (customMessage) {
      if (bodyEl) bodyEl.textContent = customMessage;
    } else {
      if (bodyEl) bodyEl.textContent = I18N.t("private_modal_desc");
    }
    modal.classList.remove("hidden");
  },

  detectPlatformFromUrl(url) {
    const lower = url.toLowerCase();
    let matched = null;
    if (lower.includes("youtube.com") || lower.includes("youtu.be")) {
      matched = "youtube";
    } else if (lower.includes("tiktok.com")) {
      matched = "tiktok";
    } else if (lower.includes("instagram.com")) {
      matched = "instagram";
    } else if (lower.includes("facebook.com") || lower.includes("fb.watch") || lower.includes("fb.com")) {
      matched = "facebook";
    }

    if (matched && matched !== this.platform) {
      this.switchPlatform(matched);
      this.addLog("info", `💡 Detected ${matched.toUpperCase()} URL, automatically switched tab.`);
    }
  },

  switchPlatform(plat) {
    this.platform = plat;
    this.currentView = plat;

    // Update sidebar navigation tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
      tab.classList.toggle("active", tab.dataset.platform === plat);
    });

    // Update view panels
    document.querySelectorAll(".view-panel").forEach(panel => {
      panel.classList.remove("active");
    });

    const targetPanel = document.getElementById(`view-${plat}`);
    if (targetPanel) {
      targetPanel.classList.add("active");
    }

    this.updatePlatformUI();
  },

  switchView(view) {
    this.currentView = view;

    // Update sidebar navigation tabs
    document.querySelectorAll(".nav-tab").forEach(tab => {
      tab.classList.toggle("active", tab.dataset.view === view);
    });

    // Update view panels
    document.querySelectorAll(".view-panel").forEach(panel => {
      panel.classList.remove("active");
    });

    const targetPanel = document.getElementById(`view-${view}`);
    if (targetPanel) {
      targetPanel.classList.add("active");
    }

    if (view === "settings") {
      this.loadSettings();
    } else if (view === "history") {
      this.loadHistory();
    } else if (view === "downloads") {
      this.renderActiveTasksView();
    }
  },

  updatePlatformUI() {
    const lang = I18N.currentLang;
    const dict = I18N.translations[lang] || I18N.translations["en"];
    const platDict = dict.platforms_info[this.platform];
    if (!platDict) return;

    const titleEl = document.getElementById("header-platform-title");
    const subEl = document.getElementById("header-platform-sub");
    if (titleEl) titleEl.textContent = platDict.title;
    if (subEl) subEl.textContent = platDict.sub;
  },

  resetPreview(plat) {
    this.platformStates[plat].metadata = null;
    const previewCard = document.getElementById(`preview-card-${plat}`);
    const finishCard = document.getElementById(`finish-card-${plat}`);
    if (previewCard) previewCard.classList.add("hidden");
    if (finishCard) finishCard.classList.add("hidden");
    this.closeQualityDropdown(plat);
  },

  async fetchInfo(plat) {
    const inputUrl = document.getElementById(`input-url-${plat}`);
    const url = (inputUrl ? inputUrl.value : "").trim();
    if (!url) {
      this.addLog("warning", "⚠️ Please enter or paste a media URL first.");
      return;
    }

    const btnAnalyze = document.getElementById(`btn-analyze-${plat}`);
    const spinner = document.getElementById(`analyze-spinner-${plat}`);
    const btnText = btnAnalyze ? btnAnalyze.querySelector(".btn-text") : null;

    if (btnAnalyze) btnAnalyze.disabled = true;
    if (spinner) spinner.classList.remove("hidden");
    if (btnText) btnText.textContent = I18N.t("analyzing");
    this.resetPreview(plat);

    try {
      const api = await this.getApi();
      if (api) {
        const res = await api.fetch_info(plat, url);
        if (res && res.success) {
          this.displayMetadata(plat, res);
        } else {
          if (res && res.is_private) {
            this.showPrivateModal(res.error);
          }
          this.addLog("error", res ? (res.error || "Failed to retrieve metadata.") : "Connection error.");
        }
      } else {
        this.addLog("error", "❌ Engine initializing. Please try again in a few seconds.");
      }
    } catch (err) {
      this.addLog("error", `❌ Error: ${err.message || err}`);
    } finally {
      if (btnAnalyze) btnAnalyze.disabled = false;
      if (spinner) spinner.classList.add("hidden");
      if (btnText) btnText.textContent = I18N.t("analyze_media");
    }
  },

  displayMetadata(plat, data) {
    this.platformStates[plat].metadata = data;

    const previewCard = document.getElementById(`preview-card-${plat}`);
    const thumbImg = document.getElementById(`media-thumb-${plat}`);
    const titleEl = document.getElementById(`media-title-${plat}`);
    const uploaderEl = document.getElementById(`media-uploader-name-${plat}`);
    const durationEl = document.getElementById(`media-duration-${plat}`);

    if (thumbImg) {
      const fallbackSvg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225" viewBox="0 0 400 225"><defs><linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%230f1c30"/><stop offset="100%" stop-color="%23060c18"/></linearGradient></defs><rect width="400" height="225" fill="url(%23bg)"/><circle cx="200" cy="112" r="38" fill="rgba(0,242,254,0.12)" stroke="rgba(0,242,254,0.4)" stroke-width="2"/><polygon points="193,98 217,112 193,126" fill="%2300f2fe"/></svg>`;
      thumbImg.onerror = () => {
        thumbImg.src = fallbackSvg;
      };
      thumbImg.src = data.thumbnail || fallbackSvg;
    }
    if (titleEl) titleEl.textContent = data.title || "Media File";
    if (uploaderEl) uploaderEl.textContent = data.uploader || "Creator";
    if (durationEl) {
      durationEl.textContent = data.duration_str || "";
      durationEl.style.display = data.duration_str ? "block" : "none";
    }

    // Configure Format buttons availability for this platform
    const btnVideo = document.getElementById(`btn-format-video-${plat}`);
    const btnAudio = document.getElementById(`btn-format-audio-${plat}`);
    const btnImage = document.getElementById(`btn-format-image-${plat}`);

    if (data.has_video === false && data.has_image) {
      if (btnVideo) btnVideo.classList.add("hidden");
      if (btnImage) btnImage.classList.remove("hidden");
      this.setFormat(plat, "image");
    } else {
      if (btnVideo) btnVideo.classList.remove("hidden");
      if (btnImage) {
        btnImage.classList.toggle("hidden", !data.has_image && plat !== "instagram");
      }
      this.setFormat(plat, "video");
    }

    // Populate Custom Quality Dropdown
    this.populateQualityDropdown(plat, data.qualities || []);

    if (previewCard) {
      previewCard.classList.remove("hidden");
      previewCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  },

  populateQualityDropdown(plat, qualities) {
    const menu = document.getElementById(`quality-dropdown-menu-${plat}`);
    const hiddenInput = document.getElementById(`select-quality-${plat}`);
    const badgeEl = document.getElementById(`selected-res-badge-${plat}`);
    const textEl = document.getElementById(`selected-quality-text-${plat}`);

    if (!menu) return;
    menu.innerHTML = "";

    if (!qualities || qualities.length === 0) {
      qualities = [{ value: "best", label: "Auto Best Quality", height: 0 }];
    }

    qualities.forEach((q, idx) => {
      const item = document.createElement("div");
      item.className = `dropdown-item ${idx === 0 ? "active" : ""}`;
      item.dataset.value = q.value;
      item.dataset.label = q.label;

      let badgeText = "HD";
      let badgeClass = "res-badge";
      if (q.height >= 2160) {
        badgeText = "4K";
        badgeClass = "res-badge badge-uhd";
      } else if (q.height >= 1440) {
        badgeText = "2K";
        badgeClass = "res-badge badge-qhd";
      } else if (q.height >= 1080) {
        badgeText = "FHD";
      } else if (q.height > 0) {
        badgeText = `${q.height}p`;
      }

      item.dataset.badge = badgeText;
      item.dataset.badgeClass = badgeClass;

      item.innerHTML = `
        <div style="display: flex; align-items: center; gap: 8px;">
          <span class="${badgeClass}">${badgeText}</span>
          <span>${q.label}</span>
        </div>
        <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="check-icon ${idx === 0 ? "" : "hidden"}">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      `;

      item.addEventListener("click", (e) => {
        e.stopPropagation();
        this.selectQuality(plat, item);
      });

      menu.appendChild(item);
    });

    const first = qualities[0];
    if (hiddenInput) hiddenInput.value = first.value;
    if (badgeEl) badgeEl.textContent = first.height >= 2160 ? "4K" : (first.height >= 1080 ? "FHD" : "HD");
    if (textEl) textEl.textContent = first.label;
    this.platformStates[plat].quality = first.value;
  },

  selectQuality(plat, item) {
    const hiddenInput = document.getElementById(`select-quality-${plat}`);
    const badgeEl = document.getElementById(`selected-res-badge-${plat}`);
    const textEl = document.getElementById(`selected-quality-text-${plat}`);
    const menu = document.getElementById(`quality-dropdown-menu-${plat}`);

    if (menu) {
      menu.querySelectorAll(".dropdown-item").forEach(el => {
        el.classList.remove("active");
        const check = el.querySelector(".check-icon");
        if (check) check.classList.add("hidden");
      });
    }

    item.classList.add("active");
    const check = item.querySelector(".check-icon");
    if (check) check.classList.remove("hidden");

    if (hiddenInput) hiddenInput.value = item.dataset.value;
    if (badgeEl) {
      badgeEl.textContent = item.dataset.badge;
      badgeEl.className = item.dataset.badgeClass || "res-badge";
    }
    if (textEl) textEl.textContent = item.dataset.label;

    this.platformStates[plat].quality = item.dataset.value;
    this.closeQualityDropdown(plat);
  },

  toggleQualityDropdown(plat) {
    const dropdown = document.getElementById(`quality-custom-dropdown-${plat}`);
    const menu = document.getElementById(`quality-dropdown-menu-${plat}`);
    if (!menu || !dropdown) return;
    const isOpen = !menu.classList.contains("hidden");

    if (isOpen) {
      this.closeQualityDropdown(plat);
    } else {
      dropdown.classList.add("open");
      menu.classList.remove("hidden");
    }
  },

  closeQualityDropdown(plat) {
    const dropdown = document.getElementById(`quality-custom-dropdown-${plat}`);
    const menu = document.getElementById(`quality-dropdown-menu-${plat}`);
    if (dropdown) dropdown.classList.remove("open");
    if (menu) menu.classList.add("hidden");
  },

  setFormat(plat, fmt) {
    this.platformStates[plat].format = fmt;
    const btnVideo = document.getElementById(`btn-format-video-${plat}`);
    const btnAudio = document.getElementById(`btn-format-audio-${plat}`);
    const btnImage = document.getElementById(`btn-format-image-${plat}`);
    const groupQuality = document.getElementById(`group-quality-${plat}`);

    if (btnVideo) btnVideo.classList.toggle("active", fmt === "video");
    if (btnAudio) btnAudio.classList.toggle("active", fmt === "audio");
    if (btnImage) btnImage.classList.toggle("active", fmt === "image");

    if (groupQuality) {
      groupQuality.style.display = (fmt === "video") ? "flex" : "none";
    }

    const hint = document.getElementById(`quality-hint-${plat}`);
    if (hint) {
      if (fmt === "audio") {
        hint.textContent = I18N.t("quality_hint_audio");
      } else if (fmt === "image") {
        hint.textContent = I18N.t("quality_hint_image");
      } else {
        hint.textContent = I18N.t("quality_hint_video");
      }
    }
  },

  // ==========================================================================
  // UNIVERSAL QUEUE EXECUTION & SYNC
  // ==========================================================================
  async startDownload(plat) {
    const st = this.platformStates[plat];
    if (!st || !st.metadata) return;

    const inputUrl = document.getElementById(`input-url-${plat}`);
    const url = (inputUrl ? inputUrl.value : st.url).trim();
    const selectQuality = document.getElementById(`select-quality-${plat}`);
    const quality = selectQuality ? selectQuality.value : (st.quality || "best");
    const format = st.format || "video";
    const title = st.metadata.title || "";
    const thumbnail = st.metadata.thumbnail || (st.metadata.images && st.metadata.images[0]) || "";

    this.addLog("info", `🚀 Queued [${plat.toUpperCase()}]: ${title || "Media"}`);

    try {
      const api = await this.getApi();
      if (api) {
        const res = await api.start_download(plat, url, quality, format, title, thumbnail);
        if (res && res.queue) {
          this.handleQueueUpdate(res.queue);
        }
      } else {
        throw new Error("Backend engine not connected.");
      }
    } catch (err) {
      this.addLog("error", `Download queue error: ${err.message || err}`);
    }
  },

  async cancelDownload(taskId = null) {
    try {
      const api = await this.getApi();
      if (api) {
        const res = await api.cancel_download(taskId);
        if (res && res.queue) {
          this.handleQueueUpdate(res.queue);
        }
      }
    } catch (err) {
      console.error("Failed to cancel download:", err);
    }
  },

  async refreshQueue() {
    try {
      const api = await this.getApi();
      if (api && typeof api.get_queue === "function") {
        const q = await api.get_queue();
        if (q) {
          this.handleQueueUpdate(q);
        }
      }
    } catch (err) {
      console.error("Failed to refresh queue:", err);
    }
  },

  handleQueueUpdate(queueData) {
    if (!queueData) return;

    this.activeTask = queueData.active || null;
    this.queueTasks = queueData.queue || [];
    const totalCount = queueData.total || 0;

    // Update Sidebar Active Tasks Count Badge
    const taskBadge = document.getElementById("task-badge-count");
    if (taskBadge) {
      if (totalCount > 0) {
        taskBadge.textContent = totalCount;
        taskBadge.classList.remove("hidden");
      } else {
        taskBadge.classList.add("hidden");
      }
    }

    // Update Header Capsule Notification
    const headerCapsule = document.getElementById("header-task-capsule");
    const headerText = document.getElementById("header-task-text");
    if (headerCapsule && headerText) {
      if (this.activeTask) {
        headerCapsule.classList.remove("hidden");
        const pct = (this.activeTask.percent || 0).toFixed(0);
        headerText.textContent = `⬇️ Downloading (${pct}%)`;
      } else if (this.queueTasks.length > 0) {
        headerCapsule.classList.remove("hidden");
        headerText.textContent = `⏳ ${this.queueTasks.length} In Queue`;
      } else {
        headerCapsule.classList.add("hidden");
      }
    }

    // Update Active Tasks View (#view-downloads)
    this.renderActiveTasksView();

    // Update Platform-Specific Tasks Containers
    this.platforms.forEach(plat => {
      this.renderPlatformTasks(plat);
    });
  },

  renderActiveTasksView() {
    const jobCard = document.getElementById("active-job-card");
    const queueSection = document.getElementById("queue-section-wrapper");
    const queueList = document.getElementById("queue-cards-list");
    const queuePill = document.getElementById("queue-count-pill");
    const emptyState = document.getElementById("active-empty-state");

    const hasActive = Boolean(this.activeTask);
    const hasQueue = this.queueTasks.length > 0;

    if (!hasActive && !hasQueue) {
      if (jobCard) jobCard.classList.add("hidden");
      if (queueSection) queueSection.classList.add("hidden");
      if (emptyState) emptyState.classList.remove("hidden");
      return;
    }

    if (emptyState) emptyState.classList.add("hidden");

    // 1. Render Active Job Card
    if (hasActive && jobCard) {
      jobCard.classList.remove("hidden");
      const thumb = document.getElementById("active-job-thumb");
      const platPill = document.getElementById("active-job-platform");
      const titleEl = document.getElementById("active-job-title");
      const formatEl = document.getElementById("active-job-format");
      const fillEl = document.getElementById("active-job-fill");
      const pctEl = document.getElementById("active-job-percent");
      const speedEl = document.getElementById("active-job-speed");
      const etaEl = document.getElementById("active-job-eta");
      const msgEl = document.getElementById("active-job-msg");

      if (thumb) {
        const fallbackSvg = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="400" height="225" viewBox="0 0 400 225"><defs><linearGradient id="bg_act" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%230f1c30"/><stop offset="100%" stop-color="%23060c18"/></linearGradient></defs><rect width="400" height="225" fill="url(%23bg_act)"/><circle cx="200" cy="112" r="38" fill="rgba(0,242,254,0.12)" stroke="rgba(0,242,254,0.4)" stroke-width="2"/><polygon points="193,98 217,112 193,126" fill="%2300f2fe"/></svg>`;
        thumb.onerror = () => { thumb.src = fallbackSvg; };
        thumb.src = this.activeTask.thumbnail || fallbackSvg;
      }
      if (platPill) platPill.textContent = (this.activeTask.platform || "").toUpperCase();
      if (titleEl) titleEl.textContent = this.activeTask.title || "Media Stream";
      if (formatEl) formatEl.textContent = (this.activeTask.format || "MP4").toUpperCase();

      const pct = this.activeTask.percent || 0;
      if (fillEl) fillEl.style.width = `${pct}%`;
      if (pctEl) pctEl.textContent = `${pct.toFixed(1)}%`;
      if (speedEl) speedEl.textContent = this.activeTask.speed ? `Speed: ${this.activeTask.speed}` : "Speed: --";
      if (etaEl) etaEl.textContent = this.activeTask.eta ? `ETA: ${this.activeTask.eta}` : "ETA: --:--";
      if (msgEl) msgEl.textContent = this.activeTask.message || "Downloading stream...";
    } else if (jobCard) {
      jobCard.classList.add("hidden");
    }

    // 2. Render Universal Queue Stack in FIFO Sequence
    if (hasQueue && queueSection && queueList) {
      queueSection.classList.remove("hidden");
      if (queuePill) queuePill.textContent = `${this.queueTasks.length} ${I18N.t("in_queue") || "In Queue"}`;
      queueList.innerHTML = "";

      this.queueTasks.forEach((task, idx) => {
        const card = document.createElement("div");
        card.className = "queued-task-card";

        const thumb = task.thumbnail || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='72' height='44'><rect width='72' height='44' fill='%23111'/></svg>";
        const plat = (task.platform || "media").toUpperCase();
        const fmt = (task.format || "mp4").toUpperCase();
        const posText = I18N.t("queue_pos") ? I18N.t("queue_pos").replace("{pos}", idx + 1) : `#${idx + 1} IN QUEUE`;

        card.innerHTML = `
          <span class="queued-task-pos">${posText}</span>
          <img class="queued-task-thumb" src="${thumb}" alt="Thumb" />
          <div class="queued-task-info">
            <h4 class="queued-task-title" title="${this.escapeHtml(task.title || "Queued Media")}">${this.escapeHtml(task.title || "Queued Media")}</h4>
            <div class="queued-task-meta">
              <span class="platform-pill" style="font-size: 0.65rem; padding: 2px 7px;">${plat}</span>
              <span class="res-badge" style="font-size: 0.65rem; padding: 2px 6px;">${(task.quality || "HD").toUpperCase()}</span>
              <span>${fmt}</span>
              <span class="queued-task-status">• ${I18N.t("waiting_turn") || "Waiting for turn..."}</span>
            </div>
          </div>
          <button class="btn-cancel-queue" title="Cancel this queued download">
            <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
            <span>${I18N.t("cancel_queue") || "Remove"}</span>
          </button>
        `;

        const btnCancel = card.querySelector(".btn-cancel-queue");
        if (btnCancel) {
          btnCancel.addEventListener("click", () => {
            this.cancelDownload(task.id);
          });
        }

        queueList.appendChild(card);
      });
    } else if (queueSection) {
      queueSection.classList.add("hidden");
    }
  },

  renderPlatformTasks(plat) {
    const card = document.getElementById(`platform-tasks-${plat}`);
    const list = document.getElementById(`platform-tasks-list-${plat}`);
    const badge = document.getElementById(`platform-queue-badge-${plat}`);
    if (!card || !list) return;

    // Filter tasks for this platform
    const isActiveForPlat = this.activeTask && this.activeTask.platform === plat;
    const queuedForPlat = this.queueTasks.filter(t => t.platform === plat);
    const totalPlat = (isActiveForPlat ? 1 : 0) + queuedForPlat.length;

    if (totalPlat === 0) {
      card.classList.add("hidden");
      list.innerHTML = "";
      return;
    }

    card.classList.remove("hidden");
    if (badge) badge.textContent = totalPlat;
    list.innerHTML = "";

    // 1. Active Task if on this platform
    if (isActiveForPlat) {
      const activeDiv = document.createElement("div");
      activeDiv.className = "queued-task-card";
      activeDiv.style.borderColor = "rgba(0, 242, 254, 0.4)";
      activeDiv.style.background = "rgba(0, 242, 254, 0.08)";

      const pct = (this.activeTask.percent || 0).toFixed(1);
      const thumb = this.activeTask.thumbnail || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='72' height='44'><rect width='72' height='44' fill='%23111'/></svg>";

      activeDiv.innerHTML = `
        <span class="queued-task-pos" style="background: var(--accent-cyan); color: #030712;">DOWNLOADING</span>
        <img class="queued-task-thumb" src="${thumb}" alt="Thumb" />
        <div class="queued-task-info">
          <h4 class="queued-task-title">${this.escapeHtml(this.activeTask.title || "Active Media")}</h4>
          <div class="queued-task-meta">
            <span class="res-badge">${(this.activeTask.quality || "HD").toUpperCase()}</span>
            <span>${pct}%</span>
            <span>${this.activeTask.speed ? `• ${this.activeTask.speed}` : ""}</span>
          </div>
          <div class="progress-track" style="margin-top: 4px; height: 5px;">
            <div class="progress-fill" style="width: ${pct}%;"></div>
          </div>
        </div>
        <button class="btn-cancel-queue" title="Cancel active download">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
          <span>${I18N.t("cancel") || "Cancel"}</span>
        </button>
      `;

      activeDiv.querySelector(".btn-cancel-queue").addEventListener("click", () => {
        this.cancelDownload();
      });

      list.appendChild(activeDiv);
    }

    // 2. Queued items for this platform
    queuedForPlat.forEach(task => {
      // Find global position
      const globalPos = this.queueTasks.findIndex(t => t.id === task.id) + 1;
      const cardItem = document.createElement("div");
      cardItem.className = "queued-task-card";

      const thumb = task.thumbnail || "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='72' height='44'><rect width='72' height='44' fill='%23111'/></svg>";
      const posText = I18N.t("queue_pos") ? I18N.t("queue_pos").replace("{pos}", globalPos) : `#${globalPos} IN QUEUE`;

      cardItem.innerHTML = `
        <span class="queued-task-pos">${posText}</span>
        <img class="queued-task-thumb" src="${thumb}" alt="Thumb" />
        <div class="queued-task-info">
          <h4 class="queued-task-title">${this.escapeHtml(task.title || "Queued Media")}</h4>
          <div class="queued-task-meta">
            <span class="res-badge">${(task.quality || "HD").toUpperCase()}</span>
            <span class="queued-task-status">• ${I18N.t("waiting_turn") || "Waiting for turn..."}</span>
          </div>
        </div>
        <button class="btn-cancel-queue" title="Cancel this queued download">
          <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
          <span>${I18N.t("cancel_queue") || "Remove"}</span>
        </button>
      `;

      cardItem.querySelector(".btn-cancel-queue").addEventListener("click", () => {
        this.cancelDownload(task.id);
      });

      list.appendChild(cardItem);
    });
  },

  // ==========================================================================
  // HISTORY, SETTINGS, AND LOGS
  // ==========================================================================
  async loadHistory() {
    const container = document.getElementById("history-items-container");
    if (!container) return;

    try {
      const api = await this.getApi();
      if (!api) return;

      const history = await api.get_history();
      container.innerHTML = "";

      if (!history || history.length === 0) {
        container.innerHTML = `
          <div class="glass-empty-state" style="padding: 40px 20px;">
            <h4 class="empty-title">${I18N.t("no_history")}</h4>
          </div>
        `;
        return;
      }

      history.forEach(item => {
        const row = document.createElement("div");
        row.className = "history-item-row";

        const fallbackThumb = `data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="90" height="52" viewBox="0 0 90 52"><defs><linearGradient id="bg_${item.id || 'hist'}" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="%2314223d"/><stop offset="100%" stop-color="%23080e1c"/></linearGradient></defs><rect width="90" height="52" fill="url(%23bg_${item.id || 'hist'})"/><circle cx="45" cy="26" r="14" fill="rgba(0,242,254,0.15)" stroke="rgba(0,242,254,0.5)" stroke-width="1.5"/><polygon points="42,21 51,26 42,31" fill="%2300f2fe"/></svg>`;
        const thumb = item.thumbnail || fallbackThumb;
        const plat = (item.platform || "media").toUpperCase();
        const fmt = (item.format || "mp4").toUpperCase();

        row.innerHTML = `
          <div class="history-thumb">
            <img src="${thumb}" alt="" onerror="this.src='${fallbackThumb}'" />
          </div>
          <div class="history-item-info">
            <h4 class="history-item-title" title="${item.title || item.filename}">${this.escapeHtml(item.title || item.filename)}</h4>
            <div class="history-item-sub">
              <span class="platform-pill" style="font-size: 0.65rem; padding: 2px 7px;">${plat}</span>
              <span class="history-size-badge">${fmt}</span>
              <span class="history-size-badge">${item.size_str || "--"}</span>
              <span style="margin-left: auto;">${item.timestamp || ""}</span>
            </div>
          </div>
          <div class="history-actions">
            <button class="btn btn-secondary btn-sm btn-hist-file">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>${I18N.t("open_file")}</span>
            </button>
            <button class="btn btn-secondary btn-sm btn-hist-folder">
              <svg viewBox="0 0 24 24" width="13" height="13" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
              </svg>
            </button>
          </div>
        `;

        const btnFile = row.querySelector(".btn-hist-file");
        if (btnFile) {
          btnFile.addEventListener("click", () => {
            if (item.file_path) {
              api.open_file(item.file_path).then(res => {
                if (res && !res.success) {
                  this.addLog("error", `❌ ${res.error || "Cannot open file."}`);
                }
              });
            }
          });
        }

        const btnFolder = row.querySelector(".btn-hist-folder");
        if (btnFolder) {
          btnFolder.addEventListener("click", () => {
            api.open_folder(item.platform || "youtube");
          });
        }

        container.appendChild(row);
      });
    } catch (e) {
      console.error("Failed to load history:", e);
    }
  },

  async loadSettings() {
    try {
      const api = await this.getApi();
      if (!api) return;
      const cfg = await api.get_settings();
      if (cfg) {
        if (cfg.language && cfg.language !== I18N.currentLang) {
          I18N.setLanguage(cfg.language);
          this.applyTranslations();
        }

        // Folders
        const folders = cfg.download_folders || {};
        for (const [plat, path] of Object.entries(folders)) {
          const el = document.getElementById(`folder-path-${plat}`);
          if (el) el.textContent = path;
        }

        // Hardware
        const hwMode = cfg.hardware_acceleration || "auto";
        const radio = document.querySelector(`input[name='hardware_mode'][value='${hwMode}']`);
        if (radio) radio.checked = true;

        const hw = cfg.hardware;
        if (hw) {
          this.hardwareInfo = hw;
          const devEl = document.getElementById("hw-device-name");
          const badgeEl = document.getElementById("hw-badge");
          const footerStatus = document.getElementById("footer-status-text");

          if (hw.has_nvidia && hw.nvenc_supported) {
            if (devEl) devEl.textContent = `${hw.gpu_name} (NVENC)`;
            if (badgeEl) {
              badgeEl.textContent = "NVENC READY";
              badgeEl.className = "hw-badge";
            }
            if (footerStatus) footerStatus.innerHTML = `⚡ GPU NVENC: <strong>${hw.gpu_name}</strong>`;
          } else {
            if (devEl) devEl.textContent = "CPU Software Encoding";
            if (badgeEl) {
              badgeEl.textContent = "CPU MODE";
              badgeEl.className = "hw-badge hw-badge-cpu";
            }
            if (footerStatus) footerStatus.textContent = "CPU Standard Mode • Hardware Ready";
          }
        }
      }
    } catch (err) {
      console.error("Failed to load settings:", err);
    }
  },

  async saveHardwareMode(mode) {
    const api = await this.getApi();
    if (api) {
      const cfg = await api.get_settings();
      if (cfg) {
        cfg.hardware_acceleration = mode;
        await api.save_settings(cfg);
        this.addLog("info", `⚡ Hardware mode changed to: ${mode.toUpperCase()}`);
      }
    }
  },

  async openFolder(platform) {
    const api = await this.getApi();
    if (api) {
      await api.open_folder(platform);
    }
  },

  async chooseFolder(platform) {
    const api = await this.getApi();
    if (api) {
      const res = await api.choose_folder(platform);
      if (res && res.success) {
        const el = document.getElementById(`folder-path-${platform}`);
        if (el) el.textContent = res.path;
      }
    }
  },

  async checkUpdate() {
    const api = await this.getApi();
    if (!api) return;
    const btn = document.getElementById("btn-check-update");
    const btnUpdate = document.getElementById("btn-run-update");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Checking...";
    }

    try {
      const res = await api.check_ytdlp_update();
      if (res) {
        const curVer = document.getElementById("ytdlp-current-version");
        if (curVer) curVer.textContent = `v${res.current_version}`;
        if (res.has_update && btnUpdate) {
          btnUpdate.classList.remove("hidden");
          btnUpdate.textContent = `Update to v${res.latest_version}`;
        }
      }
    } finally {
      if (btn) {
        btn.disabled = false;
        btn.textContent = I18N.t("check_updates");
      }
    }
  },

  async runUpdate() {
    const api = await this.getApi();
    if (!api) return;
    const btn = document.getElementById("btn-run-update");
    if (btn) {
      btn.disabled = true;
      btn.textContent = "Updating...";
    }
    await api.update_ytdlp();
  },

  addLog(level, message, timestamp = null) {
    const time = timestamp || new Date().toTimeString().split(" ")[0];
    const logObj = { level, message, timestamp: time };
    this.logEntries.push(logObj);

    const stream = document.getElementById("log-stream");
    if (!stream) return;

    const entry = document.createElement("div");
    entry.className = `log-entry log-${level}`;

    const iconMap = {
      info: "ℹ️",
      success: "✅",
      warning: "⚠️",
      error: "❌"
    };

    entry.innerHTML = `
      <span class="log-time">${time}</span>
      <span class="log-icon">${iconMap[level] || "💬"}</span>
      <span class="log-msg">${this.escapeHtml(message)}</span>
    `;

    stream.appendChild(entry);
    stream.scrollTop = stream.scrollHeight;

    const countWord = I18N.t("messages_count") || "messages";
    const countEl = document.getElementById("log-count");
    if (countEl) countEl.textContent = `${this.logEntries.length} ${countWord}`;
  },

  clearLogs() {
    this.logEntries = [];
    const stream = document.getElementById("log-stream");
    if (stream) stream.innerHTML = "";
    const countEl = document.getElementById("log-count");
    if (countEl) countEl.textContent = `0 ${I18N.t("messages_count") || "messages"}`;
    this.addLog("info", I18N.t("cleared") || "Cleared");
  },

  copyAllLogs() {
    if (this.logEntries.length === 0) return;
    const text = this.logEntries
      .map(e => `[${e.timestamp}] [${e.level.toUpperCase()}] ${e.message}`)
      .join("\n");
    navigator.clipboard.writeText(text);
    this.addLog("success", `📋 ${I18N.t("copied") || "Copied"}`);
  },

  escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.innerText = str;
    return div.innerHTML;
  }
};

// ============================================================================
// Global Callbacks from Python Backend
// ============================================================================
window.onLogEvent = function(logData) {
  if (logData) {
    app.addLog(logData.level, logData.message, logData.timestamp);
  }
};

window.onQueueUpdate = function(queueData) {
  if (queueData) {
    app.handleQueueUpdate(queueData);
  }
};

window.onDownloadProgress = function(data) {
  if (!data) return;
  const percent = data.percent || 0;
  
  if (app.activeTask) {
    app.activeTask.percent = percent;
    app.activeTask.speed = data.speed || "";
    app.activeTask.eta = data.eta || "";
    app.activeTask.message = data.message || "";
    
    // Update Active Tasks View
    const fillEl = document.getElementById("active-job-fill");
    const pctEl = document.getElementById("active-job-percent");
    const speedEl = document.getElementById("active-job-speed");
    const etaEl = document.getElementById("active-job-eta");
    const msgEl = document.getElementById("active-job-msg");

    if (fillEl) fillEl.style.width = `${percent}%`;
    if (pctEl) pctEl.textContent = `${percent.toFixed(1)}%`;
    if (speedEl && data.speed) speedEl.textContent = `Speed: ${data.speed}`;
    if (etaEl && data.eta) etaEl.textContent = `ETA: ${data.eta}`;
    if (msgEl && data.message) msgEl.textContent = data.message;

    // Also update capsule notification
    const headerText = document.getElementById("header-task-text");
    if (headerText) {
      headerText.textContent = `⬇️ Downloading (${percent.toFixed(0)}%)`;
    }

    // Refresh platform tasks active progress bar
    if (app.activeTask.platform) {
      app.renderPlatformTasks(app.activeTask.platform);
    }
  }
};

window.onDownloadComplete = function(result) {
  const filePath = result ? result.file_path : null;
  app.downloadedFilePath = filePath;
  const plat = result ? (result.platform || app.platform) : app.platform;

  if (app.platformStates[plat]) {
    app.platformStates[plat].downloadedFilePath = filePath;
  }

  // Show finish card on that platform's view
  const finishCard = document.getElementById(`finish-card-${plat}`);
  const finishFilename = document.getElementById(`finish-filename-${plat}`);
  if (finishCard) {
    finishCard.classList.remove("hidden");
    if (finishFilename && result) {
      finishFilename.textContent = result.filename || (filePath ? filePath.split(/[\\/]/).pop() : "media.mp4");
    }
  }

  // Refresh history and queue
  app.loadHistory();
  app.refreshQueue();
};

window.onDownloadFailed = function(result) {
  const errMsg = result ? (result.error || "Download encountered an error.") : "Download failed.";
  app.addLog("error", `❌ ${errMsg}`);
  app.refreshQueue();
};

document.addEventListener("DOMContentLoaded", () => {
  app.init();
});
