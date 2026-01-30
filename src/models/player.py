from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Player:
    # Api struktur
    player_id: int
    name: str
    position: str
    nationality: str
    date_of_birth: Optional[str] = None
    shirt_number: Optional[int] = None

    @property  
    def age(self) -> Optional[int]:
        if not self.date_of_birth:
            return None
        try:
            birth = date.fromisoformat(self.date_of_birth)
            today = date.today()
            age = today.year - birth.year

            if (today.month, today.day) < (birth.month, birth.day): 
                age -= 1

            return age
        except (ValueError, TypeError):
            return None
        
    @property
    def display_number(self) -> str:
        
        if self.shirt_number is None:
            return "N/A"
        return f"#{self.shirt_number}"
    
    @property
    def display_position(self) -> str:

        positions = self.position.lower()

        if 'goal' in positions and 'keeper' in positions:
            return "Goalkeeper"
        elif 'back' in positions:
            return "Defender"
        elif 'mid' in positions:
            return 'Midfielder'
        else:
            return "Forward"
        
    @property
    def is_goalkeeper(self) -> bool:
        return self.display_position == "Goalkeeper"

    @property
    def is_defender(self) -> bool:
        return self.display_position == "Defender"

    @property
    def is_midfielder(self) -> bool:
        return self.display_position == "Midfielder"

    @property
    def is_forward(self) -> bool:
        return self.display_position == "Forward"
        
    @classmethod
    def from_api_squad(cls, data: dict) -> 'Player':
    
        return cls(
            player_id=data['id'],
            name=data['name'],
            position=data.get('position', 'Unknown'),
            nationality=data.get('nationality', ''),
            date_of_birth=data.get('dateOfBirth'),
            shirt_number=data.get('shirtNumber')
        )
    
    def to_dict(self) -> dict:
        return {
            'player_id': self.player_id,
            'name': self.name,
            'position': self.position,
            'display_position': self.display_position,  
            'nationality': self.nationality,
            'date_of_birth': self.date_of_birth,
            'age': self.age,                             
            'shirt_number': self.shirt_number,
            'display_number': self.display_number       
        }
    
    def __repr__(self) -> str:
        number = self.display_number
        return f"Player(name='{self.name}', position='{self.position}', {number})"