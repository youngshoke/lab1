"""Векторный график экспериментального и теоретического ускорения."""

from pathlib import Path

from reportlab.graphics import renderPDF
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.shapes import Drawing, Line, String
from reportlab.lib import colors

from .analytics.parallel import Measurement, amdal


def build_graph(rows: tuple[Measurement, ...], fraction: float) -> Drawing:
    """Построить график ускорения со шкалами и легендой."""
    drawing = Drawing(450, 239)
    chart = LinePlot()
    chart.x, chart.y, chart.width, chart.height = 48, 43, 370, 150
    workers = (1, 2, 4, 8)
    baseline = rows[0].seconds
    chart.data = [
        [(row.workers, baseline / row.seconds) for row in rows if row.method == method]
        for method in ("thread", "process")
    ] + [[(n, amdal(n, fraction)) for n in workers]]
    chart.xValueAxis.valueMin = 1
    chart.xValueAxis.valueMax = 8
    chart.xValueAxis.valueSteps = list(workers)
    chart.yValueAxis.valueMin = 0
    chart.yValueAxis.visibleGrid = True
    chart.yValueAxis.gridStrokeColor = colors.HexColor("#dce2eb")
    legend = (
        ("Threads", colors.HexColor("#ae4c14")),
        ("Processes", colors.HexColor("#12679c")),
        ("Amdahl", colors.HexColor("#374151")),
    )
    for index, (label, color) in enumerate(legend):
        chart.lines[index].strokeColor = color
        chart.lines[index].strokeWidth = 1.7
        x = 74 + index * 117
        drawing.add(Line(x, 219, x + 19, 219, strokeColor=color, strokeWidth=1.7))
        drawing.add(String(x + 25, 216, label, fontName="Helvetica", fontSize=10))
    chart.lines[2].strokeDashArray = (5, 3)
    drawing.add(chart)
    drawing.add(String(233, 14, "Workers", textAnchor="middle", fontSize=10))
    drawing.add(String(48, 197, "Speedup", fontSize=10))
    return drawing


def save_graph(rows: tuple[Measurement, ...], fraction: float, path: Path) -> None:
    """Записать векторный график в PDF."""
    renderPDF.drawToFile(build_graph(rows, fraction), str(path), "CPU speedup")
