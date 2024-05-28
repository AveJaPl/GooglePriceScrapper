from rich.progress import Progress

# Inicjalizacja globalnego obiektu Progress, który zarządza paskami postępu
progress = Progress()


def start_progress_bar(total_items):
    """Rozpoczyna pasek postępu."""
    task_id = progress.add_task("[cyan]Processing...", total=total_items)
    progress.start()
    return task_id


def update_progress_bar(task_id, advance=1):
    """Aktualizuje pasek postępu."""
    progress.update(task_id, advance=advance)


def finish_progress_bar():
    """Kończy pasek postępu."""
    progress.stop()
