from github.Issue import Issue
from github.IssueComment import IssueComment

from validator.report import ValidationReport

BOT_COMMENT_HEADER = "## Validation history"
BOT_COMMENT_SENTINEL = "<!-- geojupyter-initiatives-validator -->"
REPORT_START_SENTINEL = "<!-- report-start -->"


def _find_bot_comment(issue: Issue) -> IssueComment | None:
    """Find an existing bot comment, if any exists."""
    for comment in issue.get_comments():
        if BOT_COMMENT_SENTINEL in comment.body:
            return comment

    return None


def _parse_comment_reports(comment_body: str) -> list[str]:
    """Extract existing report entries from comment body.

    Each report is introduced with a sentinel value (as HTML comment).
    """

    # Skip the anything before the first sentinel value; we just want the reports, not
    # the header.
    parts = comment_body.split(REPORT_START_SENTINEL)[1:]

    # Strip newlines from start and end of each report
    return [part.strip() for part in parts]


def _post_or_update_github_comment(*, issue: Issue, report: ValidationReport) -> None:
    existing_comment = _find_bot_comment(issue)
    new_comment_reports = [report.github_issue_message]

    if existing_comment:
        old_comment_reports = _parse_comment_reports(existing_comment.body)
        new_comment_reports.extend(old_comment_reports)

    # Prepend sentinel value to each report, and limit to 10 reports. Too many reports
    # would be really annoying.
    new_comment_reports = [
        f"{REPORT_START_SENTINEL}\n{report}" for report in new_comment_reports[:10]
    ]

    parts = [
        BOT_COMMENT_SENTINEL,
        BOT_COMMENT_HEADER,
        "",
        "\n\n".join(new_comment_reports),
        "",
    ]

    new_body = "\n".join(parts)

    if existing_comment is None:
        issue.create_comment(new_body)
        print(f"ℹ️ Created new comment in {issue.html_url}")
    else:
        existing_comment.edit(new_body)
        print(f"ℹ️ Updated comment in {issue.html_url}")
