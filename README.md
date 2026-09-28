# Spartans Chess Tournament

A modified 6x8 chess game implementation with AI players. This project implements a unique variant of chess played on a 6x8 board with a subset of traditional chess pieces.

## Game Overview

This chess variant is played on a 6x8 board with the following pieces:
- Pawns (♟/♙)
- Knights (♞/♘)
- Bishops (♝/♗)
- Rooks (♜/♖)
- Kings (♚/♔)

The game follows modified chess rules and includes features like:
- Bullet chess format (1-minute time control)
- Point-based scoring system
- AI player implementations
- Checkmate and stalemate detection

## Project Structure

- `board.py`: Core game engine implementation with move generation and validation
- `ai_player.py`: Base class for AI player implementations
- `game_runner.py`: Game execution and visualization
- `config.py`: Game constants and configuration

### Key Components

#### Game Engine (`board.py`)
- Move validation and generation
- Check/checkmate detection
- Board state management
- Position history tracking

#### AI Player Interface (`ai_player.py`)
Base class for AI implementations with required methods:
- `get_best_move()`: Calculate and return the best move
- `evaluate_board()`: Heuristic evaluation of board positions

#### Game Runner (`game_runner.py`)
- Game visualization with Unicode chess pieces
- Time management for bullet chess games
- Score tracking and game statistics
- Move logging and display

#### Configuration (`config.py`)
- Board dimensions (6x8)
- Piece definitions and values
- Position evaluation tables
- Unicode symbols for pieces

## Piece Values
```
Pawn: 20 points
Knight: 70 points
Bishop: 70 points
Rook: 100 points
King: 300 points
```

## Scoring System
Points are awarded for:
- Capturing pieces (piece value)
- Giving check (+2 points)
- Checkmate (+300 points)

## Running the Game

To start a game between two AI players:

```python
python game_runner.py
```

The default configuration runs a 60-second bullet game between StandardPlayer and AggressivePlayer.
