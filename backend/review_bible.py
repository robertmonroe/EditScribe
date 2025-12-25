"""
CLI tool for reviewing and editing Series Bible
Interactive terminal interface
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

sys.path.append('.')

from core.models import SeriesBible, Character, Location, TimelineEvent, Object

console = Console()


class BibleReviewer:
    """Interactive CLI for reviewing and editing Series Bible"""
    
    def __init__(self, bible_path: str):
        """Load Bible from JSON file"""
        with open(bible_path, 'r') as f:
            data = json.load(f)
        self.bible = SeriesBible.from_dict(data)
        self.bible_path = bible_path
        self.modified = False
    
    def run(self):
        """Main review loop"""
        console.print(Panel.fit(
            "[bold cyan]Series Bible Review & Edit Tool[/bold cyan]\n"
            "Review the extracted entities and make corrections",
            border_style="cyan"
        ))
        
        while True:
            console.print("\n[bold]What would you like to review?[/bold]")
            console.print("1. Characters")
            console.print("2. Locations")
            console.print("3. Timeline")
            console.print("4. Objects")
            console.print("5. Save & Exit")
            console.print("6. Exit without saving")
            
            choice = Prompt.ask("Choose an option", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.review_characters()
            elif choice == "2":
                self.review_locations()
            elif choice == "3":
                self.review_timeline()
            elif choice == "4":
                self.review_objects()
            elif choice == "5":
                self.save()
                break
            elif choice == "6":
                if not self.modified or Confirm.ask("Exit without saving changes?"):
                    break
    
    def review_characters(self):
        """Review and edit characters"""
        console.print("\n[bold cyan]📚 CHARACTERS[/bold cyan]")
        
        if not self.bible.characters:
            console.print("[yellow]No characters found[/yellow]")
            return
        
        # Display table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim")
        table.add_column("Name")
        table.add_column("Age")
        table.add_column("Occupation")
        table.add_column("First Appears")
        
        for i, char in enumerate(self.bible.characters, 1):
            table.add_row(
                str(i),
                char.name,
                str(char.age) if char.age else "-",
                char.occupation or "-",
                char.first_appears or "-"
            )
        
        console.print(table)
        
        # Edit options
        console.print("\n[bold]Options:[/bold]")
        console.print("E <number> - Edit character")
        console.print("D <number> - Delete character")
        console.print("A - Add new character")
        console.print("B - Back to main menu")
        
        action = Prompt.ask("Action").strip().upper()
        
        if action.startswith("E "):
            idx = int(action.split()[1]) - 1
            if 0 <= idx < len(self.bible.characters):
                self.edit_character(idx)
        elif action.startswith("D "):
            idx = int(action.split()[1]) - 1
            if 0 <= idx < len(self.bible.characters):
                if Confirm.ask(f"Delete {self.bible.characters[idx].name}?"):
                    del self.bible.characters[idx]
                    self.modified = True
                    console.print("[green]Character deleted[/green]")
        elif action == "A":
            self.add_character()
        elif action == "B":
            return
    
    def edit_character(self, idx: int):
        """Edit a specific character"""
        char = self.bible.characters[idx]
        console.print(f"\n[bold]Editing: {char.name}[/bold]")
        
        # Edit fields
        char.name = Prompt.ask("Name", default=char.name)
        
        age_str = Prompt.ask("Age", default=str(char.age) if char.age else "")
        char.age = int(age_str) if age_str else None
        
        char.eye_color = Prompt.ask("Eye color", default=char.eye_color or "")
        char.hair = Prompt.ask("Hair", default=char.hair or "")
        char.occupation = Prompt.ask("Occupation", default=char.occupation or "")
        char.personality_traits = Prompt.ask("Personality traits", default=char.personality_traits or "")
        char.first_appears = Prompt.ask("First appears", default=char.first_appears or "")
        
        self.modified = True
        console.print("[green]Character updated[/green]")
    
    def add_character(self):
        """Add a new character"""
        console.print("\n[bold]Add New Character[/bold]")
        
        name = Prompt.ask("Name")
        age_str = Prompt.ask("Age (optional)")
        age = int(age_str) if age_str else None
        
        char = Character(
            name=name,
            age=age,
            eye_color=Prompt.ask("Eye color (optional)") or None,
            hair=Prompt.ask("Hair (optional)") or None,
            occupation=Prompt.ask("Occupation (optional)") or None,
            personality_traits=Prompt.ask("Personality traits (optional)") or None,
            first_appears=Prompt.ask("First appears (optional)") or None
        )
        
        self.bible.characters.append(char)
        self.modified = True
        console.print("[green]Character added[/green]")
    
    def review_locations(self):
        """Review and edit locations"""
        console.print("\n[bold cyan]📍 LOCATIONS[/bold cyan]")
        
        if not self.bible.locations:
            console.print("[yellow]No locations found[/yellow]")
            return
        
        for i, loc in enumerate(self.bible.locations, 1):
            console.print(f"\n{i}. [bold]{loc.name}[/bold]")
            if loc.type:
                console.print(f"   Type: {loc.type}")
            if loc.description:
                console.print(f"   Description: {loc.description}")
            if loc.first_appears:
                console.print(f"   First appears: {loc.first_appears}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def review_timeline(self):
        """Review and edit timeline"""
        console.print("\n[bold cyan]📅 TIMELINE[/bold cyan]")
        
        if not self.bible.timeline:
            console.print("[yellow]No timeline events found[/yellow]")
            return
        
        for i, event in enumerate(self.bible.timeline, 1):
            console.print(f"\n{i}. [bold]{event.date}[/bold] ({event.day_of_week})")
            for e in event.events:
                console.print(f"   • {e}")
            if event.chapter:
                console.print(f"   Chapter: {event.chapter}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def review_objects(self):
        """Review and edit objects"""
        console.print("\n[bold cyan]🎯 OBJECTS[/bold cyan]")
        
        if not self.bible.objects:
            console.print("[yellow]No objects found[/yellow]")
            return
        
        for i, obj in enumerate(self.bible.objects, 1):
            console.print(f"\n{i}. [bold]{obj.name}[/bold]")
            if obj.color:
                console.print(f"   Color: {obj.color}")
            if obj.description:
                console.print(f"   Description: {obj.description}")
            if obj.first_appears:
                console.print(f"   First appears: {obj.first_appears}")
        
        Prompt.ask("\nPress Enter to continue")
    
    def save(self):
        """Save changes to Bible"""
        if self.modified:
            with open(self.bible_path, 'w') as f:
                json.dump(self.bible.to_dict(), f, indent=2)
            console.print(f"\n[green]✅ Changes saved to {self.bible_path}[/green]")
        else:
            console.print("\n[yellow]No changes to save[/yellow]")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        console.print("[red]Usage: python review_bible.py <bible.json>[/red]")
        sys.exit(1)
    
    bible_path = sys.argv[1]
    
    if not Path(bible_path).exists():
        console.print(f"[red]File not found: {bible_path}[/red]")
        sys.exit(1)
    
    reviewer = BibleReviewer(bible_path)
    reviewer.run()


if __name__ == "__main__":
    main()
