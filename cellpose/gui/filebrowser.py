"""File browser panel for the cellpose GUI.

Provides a scrollable list of image files (with thumbnails) from the
current folder. Clicking an item emits ``file_load_requested(path)``
which the main window connects to ``io._load_image``.
"""

import os
from collections import OrderedDict

import numpy as np
from qtpy import QtCore, QtGui
from qtpy.QtCore import Qt, Signal
from qtpy.QtWidgets import (
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from cellpose.io import get_image_files

THUMB_SIZE = 56
CACHE_MAX = 500


class ThumbnailWorker(QtCore.QThread):
    """Background thread that reads image thumbnails and emits QImages."""

    thumbnailReady = Signal(int, object)  # (index, QImage)
    finished = Signal()

    def __init__(self, file_list):
        super().__init__()
        self._file_list = file_list

    def run(self):
        for idx, path in enumerate(self._file_list):
            if self.isInterruptionRequested():
                break
            qimage = _load_thumbnail(path, THUMB_SIZE)
            self.thumbnailReady.emit(idx, qimage)
        self.finished.emit()


def _load_thumbnail(path, size):
    """Read the first frame of *path* and return a square ``QImage``."""
    ext = os.path.splitext(path)[-1].lower()
    arr = None

    try:
        if ext in (".tif", ".tiff"):
            import tifffile

            with tifffile.TiffFile(path) as tif:
                arr = tif.pages[0].asarray()
        elif ext in (".png", ".jpg", ".jpeg"):
            import cv2

            bgr = cv2.imread(path, cv2.IMREAD_UNCHANGED)
            if bgr is not None:
                arr = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    except Exception:
        pass

    if arr is None:
        img = QtGui.QImage(size, size, QtGui.QImage.Format_RGB888)
        img.fill(QtGui.QColor(60, 60, 60))
        return img

    # Normalise to uint8
    arr = arr.squeeze()
    if arr.ndim == 3 and arr.shape[2] > 3:
        arr = arr[:, :, :3]
    if arr.dtype != np.uint8:
        lo, hi = arr.min(), arr.max()
        if hi > lo:
            arr = ((arr.astype(np.float32) - lo) / (hi - lo) * 255).astype(
                np.uint8
            )
        else:
            arr = np.zeros_like(arr, dtype=np.uint8)

    # Convert to RGB QImage
    if arr.ndim == 2:
        h, w = arr.shape
        contiguous = np.ascontiguousarray(arr)
        qimg = QtGui.QImage(
            contiguous.data, w, h, w, QtGui.QImage.Format_Grayscale8
        ).copy()
        qimg = qimg.convertToFormat(QtGui.QImage.Format_RGB888)
    else:
        h, w, _ = arr.shape
        contiguous = np.ascontiguousarray(arr)
        qimg = QtGui.QImage(
            contiguous.data, w, h, 3 * w, QtGui.QImage.Format_RGB888
        ).copy()

    # Scale to square thumbnail preserving aspect ratio, pad with dark bg
    scaled = qimg.scaled(
        size,
        size,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    canvas = QtGui.QImage(size, size, QtGui.QImage.Format_RGB888)
    canvas.fill(QtGui.QColor(40, 40, 40))
    painter = QtGui.QPainter(canvas)
    x = (size - scaled.width()) // 2
    y = (size - scaled.height()) // 2
    painter.drawImage(x, y, scaled)
    painter.end()
    return canvas


class FileBrowserPanel(QWidget):
    """Panel showing image files in a folder with clickable thumbnails."""

    file_load_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._file_paths = []
        self._thumb_cache = OrderedDict()
        self._worker = None
        self._current_folder = ""

        self._build_ui()
        self._apply_stylesheet()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(4, 4, 4, 4)
        outer.setSpacing(0)

        # GroupBox — gives the white border that matches all other panels
        self._group = QGroupBox("Files")
        self._group.setFont(QtGui.QFont("Arial", 11, QtGui.QFont.Bold))
        group_layout = QVBoxLayout(self._group)
        group_layout.setContentsMargins(4, 8, 4, 4)
        group_layout.setSpacing(4)

        # "Add folder" button row
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 0, 0, 0)
        add_btn = QPushButton("+")
        add_btn.setFixedSize(24, 24)
        add_btn.setToolTip("Add folder")
        add_btn.clicked.connect(self.add_folder)
        btn_row.addStretch()
        btn_row.addWidget(add_btn)
        group_layout.addLayout(btn_row)

        # File list
        self.list_widget = QListWidget()
        self.list_widget.setViewMode(QListWidget.ListMode)
        self.list_widget.setIconSize(QtCore.QSize(THUMB_SIZE, THUMB_SIZE))
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(2)
        self.list_widget.setWordWrap(True)
        self.list_widget.itemClicked.connect(self._on_item_clicked)
        group_layout.addWidget(self.list_widget)

        outer.addWidget(self._group)
        self.setMinimumWidth(160)

    def _apply_stylesheet(self):
        self.setStyleSheet(
            """
            QGroupBox {
                border: 1px solid white;
                color: rgb(255, 255, 255);
                border-radius: 6px;
                margin-top: 8px;
                padding: 0px 0px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QListWidget {
                background-color: rgb(30, 30, 30);
                border: none;
                color: white;
                font-size: 11px;
            }
            QListWidget::item {
                padding: 2px;
                border-bottom: 1px solid rgb(50, 50, 50);
            }
            QListWidget::item:hover {
                background-color: rgb(50, 50, 60);
            }
            QListWidget::item:selected {
                background-color: rgb(42, 130, 218);
                color: white;
            }
            QPushButton {
                background-color: rgb(50, 50, 50);
                color: white;
                border: 1px solid rgb(80, 80, 80);
                border-radius: 3px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgb(70, 70, 70);
            }
            """
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def refresh(self, folder):
        """Repopulate the list with image files from *folder*.

        No-op if *folder* is already displayed.
        """
        if folder == self._current_folder:
            return
        self._current_folder = folder
        self._stop_worker()
        self._file_paths = []
        self.list_widget.clear()

        try:
            paths = get_image_files(folder, "_masks")
        except (ValueError, Exception):
            return

        self._file_paths = list(paths)
        self._populate_items(self._file_paths)
        self._start_worker(0, self._file_paths)

    def highlight(self, filepath):
        """Scroll to and visually mark *filepath* as the current file."""
        filepath = os.path.normpath(filepath)
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item_path = os.path.normpath(item.data(Qt.UserRole) or "")
            if item_path == filepath:
                self.list_widget.setCurrentItem(item)
                self.list_widget.scrollToItem(
                    item, QListWidget.EnsureVisible
                )
                break

    def add_folder(self):
        """Open a folder dialog and append its image files to the list."""
        folder = QFileDialog.getExistingDirectory(
            self, "Add folder", self._current_folder or ""
        )
        if not folder:
            return

        try:
            new_paths = list(get_image_files(folder, "_masks"))
        except (ValueError, Exception):
            return

        existing = set(self._file_paths)
        added = [p for p in new_paths if p not in existing]
        if not added:
            return

        start_idx = len(self._file_paths)
        self._file_paths.extend(added)

        # Add separator
        sep = QListWidgetItem(f"── {os.path.basename(folder)} ──")
        sep.setFlags(Qt.NoItemFlags)
        sep.setForeground(QtGui.QBrush(QtGui.QColor(120, 120, 120)))
        self.list_widget.addItem(sep)

        self._populate_items(added, offset=start_idx)
        self._start_worker(start_idx, added)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _populate_items(self, paths, offset=0):
        """Add placeholder list items for *paths*."""
        placeholder = QtGui.QPixmap(THUMB_SIZE, THUMB_SIZE)
        placeholder.fill(QtGui.QColor(50, 50, 50))
        placeholder_icon = QtGui.QIcon(placeholder)

        for idx, path in enumerate(paths):
            cached = self._thumb_cache.get(path)
            icon = (
                QtGui.QIcon(QtGui.QPixmap.fromImage(cached))
                if cached is not None
                else placeholder_icon
            )
            item = QListWidgetItem(icon, os.path.basename(path))
            item.setData(Qt.UserRole, path)
            item.setToolTip(path)
            self.list_widget.addItem(item)

    def _start_worker(self, start_idx, paths):
        """Launch a thumbnail worker for *paths* starting at list index *start_idx*."""
        worker = ThumbnailWorker(paths)
        worker.thumbnailReady.connect(
            lambda idx, img, offset=start_idx: self._set_thumbnail(
                idx + offset, img
            )
        )
        worker.finished.connect(self._on_worker_finished)
        self._worker = worker
        worker.start()

    def _stop_worker(self):
        if self._worker is not None and self._worker.isRunning():
            self._worker.requestInterruption()
            self._worker.wait(200)
        self._worker = None

    def _on_item_clicked(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.file_load_requested.emit(path)

    def _set_thumbnail(self, list_idx, qimage):
        """Set the icon for list item *list_idx* from a ``QImage``."""
        # Adjust for any separator items that were inserted
        # We iterate to find the item whose UserRole index matches
        actual_idx = 0
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) is None:
                continue  # separator
            if actual_idx == list_idx:
                pixmap = QtGui.QPixmap.fromImage(qimage)
                item.setIcon(QtGui.QIcon(pixmap))
                # Cache by path
                path = item.data(Qt.UserRole)
                if path:
                    self._thumb_cache[path] = qimage
                    if len(self._thumb_cache) > CACHE_MAX:
                        self._thumb_cache.popitem(last=False)
                return
            actual_idx += 1

    def _on_worker_finished(self):
        if self._worker is self.sender():
            self._worker = None

    def closeEvent(self, event):
        self._stop_worker()
        super().closeEvent(event)
