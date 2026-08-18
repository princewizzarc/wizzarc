import math

from PySide6.QtCore import (
    Qt,
    QTimer,
    QPointF,
    QRectF,
)

from PySide6.QtGui import (
    QColor,
    QPainter,
    QPen,
    QRadialGradient,
    QLinearGradient,
)

from PySide6.QtWidgets import QWidget


class AIOrb(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setMinimumSize(
            330,
            330
        )

        self.setMaximumSize(
            430,
            430
        )

        self.angle = 0.0
        self.angle_secondary = 0.0
        self.pulse = 0.0
        self.wave = 0.0
        self.success_progress = 0.0

        self.state = "idle"

        self.timer = QTimer(self)
        self.timer.timeout.connect(
            self.update_animation
        )
        self.timer.start(
            30
        )

    # =====================================================
    # STATE
    # =====================================================

    def set_state(
        self,
        state
    ):

        allowed = [
            "idle",
            "listening",
            "speaking",
            "thinking",
            "success",
        ]

        if state not in allowed:
            state = "idle"

        if (
            state == "success"
            and
            self.state != "success"
        ):
            self.success_progress = 0.0

        self.state = state
        self.update()

    # =====================================================
    # ANIMATION
    # =====================================================

    def update_animation(self):

        if self.state == "thinking":
            speed = 4.0
            pulse_speed = 0.12

        elif self.state == "listening":
            speed = 2.7
            pulse_speed = 0.14

        elif self.state == "speaking":
            speed = 3.0
            pulse_speed = 0.18

        elif self.state == "success":
            speed = 1.7
            pulse_speed = 0.10
            self.success_progress = min(
                1.0,
                self.success_progress + 0.05
            )

        else:
            speed = 1.25
            pulse_speed = 0.055

        self.angle = (
            self.angle + speed
        ) % 360

        self.angle_secondary -= (
            speed * 0.68
        )

        if self.angle_secondary <= -360:
            self.angle_secondary += 360

        self.pulse += pulse_speed
        self.wave += pulse_speed * 1.5

        self.update()

    # =====================================================
    # COLORS
    # =====================================================

    def get_state_colors(self):

        if self.state == "listening":
            return (
                QColor(180, 65, 255),
                QColor(45, 150, 255),
            )

        if self.state == "speaking":
            return (
                QColor(220, 70, 255),
                QColor(65, 120, 255),
            )

        if self.state == "thinking":
            return (
                QColor(160, 55, 255),
                QColor(35, 125, 255),
            )

        if self.state == "success":
            return (
                QColor(75, 235, 145),
                QColor(35, 180, 120),
            )

        return (
            QColor(176, 65, 255),
            QColor(45, 125, 255),
        )

    # =====================================================
    # HELPERS
    # =====================================================

    def draw_ring(
        self,
        painter,
        center,
        rx,
        ry,
        color,
        alpha,
        width=1.5
    ):

        pen = QPen(
            QColor(
                color.red(),
                color.green(),
                color.blue(),
                alpha
            )
        )

        pen.setWidthF(
            width
        )

        painter.setPen(
            pen
        )

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.drawEllipse(
            QRectF(
                center.x() - rx,
                center.y() - ry,
                rx * 2,
                ry * 2
            )
        )

    # =====================================================
    # PAINT
    # =====================================================

    def paintEvent(
        self,
        event
    ):

        painter = QPainter(
            self
        )

        painter.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        w = self.width()
        h = self.height()
        base = min(w, h)

        primary, secondary = (
            self.get_state_colors()
        )

        # Main orb is slightly higher to leave room
        # for the holographic platform below.
        center = QPointF(
            w / 2,
            h * 0.40
        )

        sphere_radius = (
            base * 0.205
            + math.sin(self.pulse)
            * base * 0.006
        )

        # =================================================
        # SOFT AURA
        # =================================================

        aura = QRadialGradient(
            center,
            sphere_radius * 1.65
        )

        aura.setColorAt(
            0.0,
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                72
            )
        )

        aura.setColorAt(
            0.48,
            QColor(
                secondary.red(),
                secondary.green(),
                secondary.blue(),
                35
            )
        )

        aura.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            aura
        )

        painter.drawEllipse(
            center,
            sphere_radius * 1.65,
            sphere_radius * 1.65
        )

        # =================================================
        # ENERGY BEAM TO PLATFORM
        # =================================================

        beam_top = (
            center.y()
            + sphere_radius * 0.82
        )

        beam_bottom = (
            h * 0.73
        )

        beam = QLinearGradient(
            center.x(),
            beam_top,
            center.x(),
            beam_bottom
        )

        beam.setColorAt(
            0.0,
            QColor(
                235,
                225,
                255,
                100
            )
        )

        beam.setColorAt(
            0.45,
            QColor(
                110,
                95,
                255,
                65
            )
        )

        beam.setColorAt(
            1.0,
            QColor(
                65,
                155,
                255,
                0
            )
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            beam
        )

        beam_width = (
            base * 0.026
            + (
                math.sin(
                    self.pulse * 1.4
                )
                + 1
            )
            * base * 0.004
        )

        painter.drawRect(
            QRectF(
                center.x() - beam_width / 2,
                beam_top,
                beam_width,
                beam_bottom - beam_top
            )
        )

        # =================================================
        # HOLOGRAPHIC PLATFORM
        # =================================================

        platform_center = QPointF(
            center.x(),
            h * 0.745
        )

        platform_glow = QRadialGradient(
            platform_center,
            base * 0.29
        )

        platform_glow.setColorAt(
            0.0,
            QColor(
                100,
                85,
                255,
                70
            )
        )

        platform_glow.setColorAt(
            0.55,
            QColor(
                50,
                120,
                255,
                25
            )
        )

        platform_glow.setColorAt(
            1.0,
            QColor(0, 0, 0, 0)
        )

        painter.setBrush(
            platform_glow
        )

        painter.drawEllipse(
            QRectF(
                platform_center.x()
                - base * 0.30,
                platform_center.y()
                - base * 0.085,
                base * 0.60,
                base * 0.17
            )
        )

        platform_rings = [
            (0.28, 0.060, 105, 1.0),
            (0.235, 0.050, 145, 1.3),
            (0.185, 0.042, 185, 1.6),
            (0.125, 0.032, 110, 1.0),
        ]

        for index, (
            rx_scale,
            ry_scale,
            alpha,
            pen_width
        ) in enumerate(
            platform_rings
        ):

            color = (
                primary
                if index % 2 == 0
                else secondary
            )

            phase_shift = (
                math.sin(
                    self.pulse
                    + index
                )
                * base
                * 0.004
            )

            self.draw_ring(
                painter,
                QPointF(
                    platform_center.x(),
                    platform_center.y()
                    + phase_shift
                ),
                base * rx_scale,
                base * ry_scale,
                color,
                alpha,
                pen_width
            )

        # Rotating platform arcs
        for index in range(3):

            rx = base * (
                0.19
                + index * 0.045
            )

            ry = base * (
                0.043
                + index * 0.009
            )

            arc_pen = QPen(
                QColor(
                    (
                        primary
                        if index % 2 == 0
                        else secondary
                    ).red(),
                    (
                        primary
                        if index % 2 == 0
                        else secondary
                    ).green(),
                    (
                        primary
                        if index % 2 == 0
                        else secondary
                    ).blue(),
                    215 - index * 35
                )
            )

            arc_pen.setWidthF(
                2.0 - index * 0.25
            )

            painter.setPen(
                arc_pen
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            painter.drawArc(
                QRectF(
                    platform_center.x() - rx,
                    platform_center.y() - ry,
                    rx * 2,
                    ry * 2
                ),
                int(
                    (
                        -self.angle
                        + index * 80
                    )
                    * 16
                ),
                int(
                    (
                        95
                        + index * 22
                    )
                    * 16
                )
            )

        # Platform particles
        for index in range(6):

            a = math.radians(
                self.angle
                + index * 60
            )

            rx = base * (
                0.20
                + (
                    index % 3
                )
                * 0.025
            )

            ry = base * (
                0.045
                + (
                    index % 2
                )
                * 0.010
            )

            x = (
                platform_center.x()
                + math.cos(a)
                * rx
            )

            y = (
                platform_center.y()
                + math.sin(a)
                * ry
            )

            dot_color = QColor(
                primary
                if index % 2 == 0
                else secondary
            )

            dot_color.setAlpha(
                235
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                dot_color
            )

            dot_size = (
                base * 0.009
                + (
                    math.sin(
                        self.pulse
                        + index
                    )
                    + 1
                )
                * base * 0.002
            )

            painter.drawEllipse(
                QPointF(
                    x,
                    y
                ),
                dot_size,
                dot_size
            )

        # =================================================
        # GLOSSY SPHERE
        # =================================================

        sphere_gradient = QRadialGradient(
            QPointF(
                center.x() - sphere_radius * 0.30,
                center.y() - sphere_radius * 0.38
            ),
            sphere_radius * 1.35
        )

        sphere_gradient.setColorAt(
            0.0,
            QColor(
                88,
                94,
                155,
                235
            )
        )

        sphere_gradient.setColorAt(
            0.20,
            QColor(
                25,
                28,
                58,
                250
            )
        )

        sphere_gradient.setColorAt(
            0.68,
            QColor(
                7,
                8,
                22,
                255
            )
        )

        sphere_gradient.setColorAt(
            1.0,
            QColor(
                2,
                3,
                10,
                255
            )
        )

        painter.setPen(
            Qt.PenStyle.NoPen
        )

        painter.setBrush(
            sphere_gradient
        )

        painter.drawEllipse(
            center,
            sphere_radius,
            sphere_radius
        )

        # Dual neon rim
        rim_rect = QRectF(
            center.x() - sphere_radius,
            center.y() - sphere_radius,
            sphere_radius * 2,
            sphere_radius * 2
        )

        rim_pen = QPen(
            QColor(
                primary.red(),
                primary.green(),
                primary.blue(),
                245
            )
        )

        rim_pen.setWidthF(
            4.0
        )

        painter.setPen(
            rim_pen
        )

        painter.setBrush(
            Qt.BrushStyle.NoBrush
        )

        painter.drawArc(
            rim_rect,
            int(35 * 16),
            int(165 * 16)
        )

        rim_pen_2 = QPen(
            QColor(
                secondary.red(),
                secondary.green(),
                secondary.blue(),
                245
            )
        )

        rim_pen_2.setWidthF(
            4.0
        )

        painter.setPen(
            rim_pen_2
        )

        painter.drawArc(
            rim_rect,
            int(215 * 16),
            int(175 * 16)
        )

        # Gloss reflections
        painter.setPen(
            Qt.PenStyle.NoPen
        )

        gloss = QRadialGradient(
            QPointF(
                center.x() - sphere_radius * 0.38,
                center.y() - sphere_radius * 0.42
            ),
            sphere_radius * 0.56
        )

        gloss.setColorAt(
            0.0,
            QColor(
                255,
                255,
                255,
                150
            )
        )

        gloss.setColorAt(
            0.45,
            QColor(
                190,
                205,
                255,
                45
            )
        )

        gloss.setColorAt(
            1.0,
            QColor(
                255,
                255,
                255,
                0
            )
        )

        painter.setBrush(
            gloss
        )

        painter.drawEllipse(
            QRectF(
                center.x()
                - sphere_radius * 0.72,
                center.y()
                - sphere_radius * 0.72,
                sphere_radius * 0.72,
                sphere_radius * 0.55
            )
        )

        # =================================================
        # FOCUS ORBIT CENTER ICON
        # =================================================

        if self.state == "success":

            check_pen = QPen(
                QColor(
                    235,
                    255,
                    245,
                    245
                )
            )

            check_pen.setWidthF(
                5.0
            )

            check_pen.setCapStyle(
                Qt.PenCapStyle.RoundCap
            )

            painter.setPen(
                check_pen
            )

            scale = (
                0.55
                + 0.45
                * self.success_progress
            )

            p1 = QPointF(
                center.x()
                - base * 0.040
                * scale,
                center.y()
            )

            p2 = QPointF(
                center.x()
                - base * 0.010
                * scale,
                center.y()
                + base * 0.030
                * scale
            )

            p3 = QPointF(
                center.x()
                + base * 0.055
                * scale,
                center.y()
                - base * 0.045
                * scale
            )

            painter.drawLine(
                p1,
                p2
            )

            painter.drawLine(
                p2,
                p3
            )

        else:

            icon_center = center

            outer_icon = (
                sphere_radius * 0.48
            )

            middle_icon = (
                sphere_radius * 0.32
            )

            inner_icon = (
                sphere_radius * 0.14
            )

            orbit_pen = QPen(
                QColor(
                    primary.red(),
                    primary.green(),
                    primary.blue(),
                    235
                )
            )

            orbit_pen.setWidthF(
                3.0
            )

            painter.setPen(
                orbit_pen
            )

            painter.setBrush(
                Qt.BrushStyle.NoBrush
            )

            painter.drawArc(
                QRectF(
                    icon_center.x()
                    - outer_icon,
                    icon_center.y()
                    - outer_icon,
                    outer_icon * 2,
                    outer_icon * 2
                ),
                int(
                    -self.angle
                    * 16
                ),
                int(
                    250
                    * 16
                )
            )

            middle_pen = QPen(
                QColor(
                    218,
                    205,
                    255,
                    225
                )
            )

            middle_pen.setWidthF(
                2.3
            )

            painter.setPen(
                middle_pen
            )

            painter.drawEllipse(
                icon_center,
                middle_icon,
                middle_icon
            )

            inner_pen = QPen(
                QColor(
                    secondary.red(),
                    secondary.green(),
                    secondary.blue(),
                    245
                )
            )

            inner_pen.setWidthF(
                3.0
            )

            painter.setPen(
                inner_pen
            )

            painter.drawEllipse(
                icon_center,
                inner_icon,
                inner_icon
            )

            painter.setPen(
                Qt.PenStyle.NoPen
            )

            painter.setBrush(
                QColor(
                    220,
                    205,
                    255,
                    240
                )
            )

            painter.drawEllipse(
                icon_center,
                sphere_radius * 0.055,
                sphere_radius * 0.055
            )

            # Tiny rotating focus point
            focus_a = math.radians(
                -self.angle_secondary
            )

            fx = (
                icon_center.x()
                + math.cos(
                    focus_a
                )
                * outer_icon
            )

            fy = (
                icon_center.y()
                + math.sin(
                    focus_a
                )
                * outer_icon
            )

            painter.setBrush(
                QColor(
                    255,
                    255,
                    255,
                    245
                )
            )

            painter.drawEllipse(
                QPointF(
                    fx,
                    fy
                ),
                base * 0.010,
                base * 0.010
            )