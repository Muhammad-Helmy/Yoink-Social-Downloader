"""
Internationalization (i18n) module for Yoink Social backend
Supported languages: en (default), id (Indonesian), es (Spanish)
"""

LOG_MESSAGES = {
    "en": {
        "ready": "Yoink Social is ready. Select a platform and paste a media URL.",
        "connected": "Connected to Python backend engine.",
        "cleared": "Log history cleared.",
        "copied": "Log history copied to clipboard!",
        "analyzing": "Analyzing {platform} link...",
        "analyzed": 'Metadata retrieved: "{title}" ({count} quality options)',
        "download_started": "Downloading {type} ({quality}) — {title}",
        "download_success": "Done! File saved: {filename}",
        "download_failed": "Download failed: {error}",
        "download_cancelled": "Download cancelled by user.",
        "cancelling": "Cancelling download process...",
        "busy": "A download is already in progress. Please wait or cancel first.",
        "empty_url": "Please paste a media URL first.",
        "folder_opened": "Opened folder: {folder}",
        "folder_changed": "Default download folder for {platform} set to: {path}",
        "ytdlp_latest": "yt-dlp extractor is up to date (v{version}).",
        "ytdlp_update_avail": "yt-dlp update available: v{latest} (installed: v{current}).",
        "ytdlp_updating": "Updating yt-dlp extractor...",
        "ytdlp_updated": "yt-dlp successfully updated! Please restart the app if needed.",
        "download_images_count": "Successfully downloaded {count} images to folder.",
        # Errors
        "err_403": "Server blocked temporary access (HTTP 403). Try again in a few moments or check yt-dlp updates in Settings.",
        "err_private": "This media is private or requires login. Yoink Social only supports public content.",
        "err_not_found": "Media not found or was removed by the author.",
        "err_bot": "Platform requested bot verification. Please wait a moment before trying this link again.",
        "err_invalid_url": "Invalid URL format for {platform}. Make sure the link is complete and correct.",
        "err_network": "Network connection error or server timed out. Check your internet connection.",
        "err_ffmpeg": "FFmpeg not detected. FFmpeg is required for merging streams and MP3 conversion.",
        "err_tiktok_extractor": "TikTok extractor encountered an issue. TikTok may have changed their layout. Check for updates.",
        "err_ig_rate_limit": "Instagram is rate-limiting downloads. Please wait 1-2 minutes before downloading again.",
        "err_no_video": "This post does not contain video streams. Switching to image download mode.",
    },
    "id": {
        "ready": "Yoink Social siap digunakan. Silakan pilih platform dan tempel URL media.",
        "connected": "Antarmuka terhubung ke Python backend engine.",
        "cleared": "Riwayat log dibersihkan.",
        "copied": "Seluruh riwayat log disalin ke clipboard!",
        "analyzing": "Menganalisis link {platform}...",
        "analyzed": 'Metadata berhasil diambil: "{title}" ({count} opsi kualitas)',
        "download_started": "Mengunduh {type} ({quality}) — {title}",
        "download_success": "Selesai! File tersimpan: {filename}",
        "download_failed": "Gagal mengunduh file: {error}",
        "download_cancelled": "Unduhan telah dibatalkan oleh pengguna.",
        "cancelling": "Membatalkan proses unduhan...",
        "busy": "Ada proses unduhan yang sedang berjalan. Tunggu atau batalkan terlebih dahulu.",
        "empty_url": "Mohon tempel (paste) URL media terlebih dahulu.",
        "folder_opened": "Membuka folder: {folder}",
        "folder_changed": "Folder unduhan {platform} diubah ke: {path}",
        "ytdlp_latest": "Modul yt-dlp sudah versi terbaru (v{version}).",
        "ytdlp_update_avail": "Tersedia update yt-dlp: v{latest} (versi saat ini: v{current}).",
        "ytdlp_updating": "Mengunduh dan memperbarui modul yt-dlp...",
        "ytdlp_updated": "Modul yt-dlp berhasil diperbarui! Silakan restart aplikasi bila diperlukan.",
        "download_images_count": "Berhasil mengunduh {count} gambar ke folder tujuan.",
        # Errors
        "err_403": "Server memblokir akses sementara (HTTP 403). Coba lagi beberapa saat atau periksa update yt-dlp di Settings.",
        "err_private": "Media ini berstatus privat atau memerlukan login. Yoink Social hanya mendukung media publik.",
        "err_not_found": "Media tidak ditemukan atau sudah dihapus oleh pemiliknya.",
        "err_bot": "Platform meminta verifikasi robot (bot check). Tunggu sejenak sebelum mencoba kembali.",
        "err_invalid_url": "Format URL tidak valid untuk {platform}. Pastikan link media sudah lengkap.",
        "err_network": "Koneksi internet bermasalah atau server tidak merespons. Periksa jaringan Anda.",
        "err_ffmpeg": "FFmpeg tidak ditemukan. Dibutuhkan FFmpeg untuk menggabungkan stream dan ekstrak MP3.",
        "err_tiktok_extractor": "Ekstraktor TikTok mengalami kendala (kemungkinan perubahan struktur TikTok). Coba periksa update di Settings.",
        "err_ig_rate_limit": "Instagram membatasi frekuensi unduhan (rate-limit). Coba jeda 1-2 menit sebelum mengunduh link berikutnya.",
        "err_no_video": "Postingan ini tidak memuat stream video. Beralih ke opsi unduh gambar.",
    },
    "es": {
        "ready": "Yoink Social está listo. Seleccione una plataforma y pegue una URL.",
        "connected": "Conectado al motor backend de Python.",
        "cleared": "Historial de registros borrado.",
        "copied": "¡Historial de registros copiado al portapapeles!",
        "analyzing": "Analizando enlace de {platform}...",
        "analyzed": 'Metadatos obtenidos: "{title}" ({count} opciones de calidad)',
        "download_started": "Descargando {type} ({quality}) — {title}",
        "download_success": "¡Listo! Archivo guardado: {filename}",
        "download_failed": "Error al descargar: {error}",
        "download_cancelled": "Descarga cancelada por el usuario.",
        "cancelling": "Cancelando proceso de descarga...",
        "busy": "Ya hay una descarga en curso. Espere o cancele primero.",
        "empty_url": "Pegue una URL de medios primero.",
        "folder_opened": "Carpeta abierta: {folder}",
        "folder_changed": "Carpeta de descarga para {platform} cambiada a: {path}",
        "ytdlp_latest": "El extractor yt-dlp está actualizado (v{version}).",
        "ytdlp_update_avail": "Actualización disponible de yt-dlp: v{latest} (instalada: v{current}).",
        "ytdlp_updating": "Actualizando extractor yt-dlp...",
        "ytdlp_updated": "¡yt-dlp actualizado con éxito! Reinicie la aplicación si es necesario.",
        "download_images_count": "Se descargaron correctamente {count} imágenes en la carpeta.",
        # Errors
        "err_403": "El servidor bloqueó el acceso temporalmente (HTTP 403). Intente nuevamente más tarde.",
        "err_private": "Este contenido es privado o requiere inicio de sesión. Yoink Social solo admite contenido público.",
        "err_not_found": "El contenido no fue encontrado o fue eliminado por el autor.",
        "err_bot": "La plataforma solicitó verificación de bot. Espere un momento antes de volver a intentarlo.",
        "err_invalid_url": "Formato de URL no válido para {platform}. Asegúrese de que el enlace sea correcto.",
        "err_network": "Error de conexión de red o tiempo de espera agotado.",
        "err_ffmpeg": "FFmpeg no encontrado. Se requiere FFmpeg para fusionar transmisiones y convertir a MP3.",
        "err_tiktok_extractor": "El extractor de TikTok encontró un problema. Verifique si hay actualizaciones.",
        "err_ig_rate_limit": "Instagram está limitando la tasa de descargas. Espere 1-2 minutos.",
        "err_no_video": "Esta publicación no contiene video. Cambiando al modo de descarga de imágenes.",
    }
}

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    lang = lang.lower()
    if lang not in LOG_MESSAGES:
        lang = "en"
    dict_lang = LOG_MESSAGES.get(lang, LOG_MESSAGES["en"])
    text = dict_lang.get(key, LOG_MESSAGES["en"].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
