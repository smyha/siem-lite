import os
from typing import Any, Dict, List, Optional


class LaTeXReportGenerator:
    """
    Generates a LaTeX report from logs, alerts, and plots.
    """

    def generate_report(
        self,
        log_df: Optional[Any],
        alerts: List[Dict[str, Any]],
        plots: Any,
        output_file: Optional[str] = None,
    ) -> str:
        """
        Generates a LaTeX report and writes it to a .tex file.
        Returns the path to the generated file.
        """
        if not output_file:
            output_file = os.path.join("reports", "security_report.tex")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w") as f:
            alert_lines = "\\newline\n".join(str(a) for a in alerts)
            latex_content = (
                "\\documentclass{article}\n"
                "\\begin{document}\n"
                "\\section*{Security Report}\n"
                "\\subsection*{Summary}\n"
                f"Total alerts: {len(alerts)}\n"
                "\\subsection*{Alerts}\n"
                f"{alert_lines}\n"
                "\\end{document}\n"
            )
            f.write(latex_content)
        return output_file
