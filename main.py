from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from dotenv import load_dotenv

from betnacional.client import BetnacionalClient

load_dotenv()

app = FastAPI(title="Betnacional SDK API", version="1.0.0")

# Setup logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger("betnacional.api_server")

# Initialize client lazily
client = None

def get_client() -> BetnacionalClient:
    global client
    if client is None:
        logger.info("Initializing BetnacionalClient in API server...")
        client = BetnacionalClient(headless_scraper=True)
        # Perform initial login
        if not client.login():
            logger.error("Initial login failed during API startup.")
            raise HTTPException(status_code=500, detail="Failed to authenticate with Betnacional")
    return client

class BetChoice(BaseModel):
    match_id: str
    choice: str  # "casa", "empate", "fora"

class BetRequest(BaseModel):
    choices: List[BetChoice]
    stake: float
    tournament_id: int = 325

@app.get("/")
def read_root():
    return {"status": "ok", "app": "betnacional-client-sdk"}

@app.get("/balance")
def get_balance():
    try:
        sdk_client = get_client()
        balance = sdk_client.get_balance()
        return {"balance": balance}
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches")
def get_matches(tournament_id: int = 325):
    try:
        sdk_client = get_client()
        league = "Brasileirão Série A" if tournament_id == 325 else "Brasileirão Série B" if tournament_id == 390 else ""
        matches = sdk_client.listar_jogos_rodada_brasileirao(tournament_id=tournament_id, league_name=league)
        return {"matches": [m.model_dump() for m in matches]}
    except Exception as e:
        logger.error(f"Error fetching matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/matches/serie-b")
def get_matches_serie_b():
    try:
        sdk_client = get_client()
        matches = sdk_client.listar_jogos_rodada_brasileirao_serie_b()
        return {"matches": [m.model_dump() for m in matches]}
    except Exception as e:
        logger.error(f"Error fetching Série B matches: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bet")
def place_bet(payload: BetRequest):
    try:
        sdk_client = get_client()
        choices_dicts = [{"match_id": item.match_id, "choice": item.choice} for item in payload.choices]
        
        result = sdk_client.multipla_rodada_resultados_brasileirao(
            choices=choices_dicts,
            stake=payload.stake,
            tournament_id=payload.tournament_id
        )
        return {
            "success": result.success,
            "bet_id": result.bet_id,
            "message": result.message
        }
    except Exception as e:
        logger.error(f"Error placing bet: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bets/history")
def get_bet_history(
    status: str = "pending",
    date_start: str = None,
    date_end: str = None,
    limit: int = 20
):
    try:
        sdk_client = get_client()
        result = sdk_client.get_bet_history(
            status=status,
            date_start=date_start,
            date_end=date_end,
            limit=limit
        )
        return {
            "bets": [b.model_dump() for b in result.bets],
            "events": [e.model_dump() for e in result.events],
            "scores": result.scores
        }
    except Exception as e:
        logger.error(f"Error fetching bet history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bets/details")
def get_bet_details(ticket_id: str):
    try:
        sdk_client = get_client()
        result = sdk_client.get_bet_details(ticket_id=ticket_id)
        return result
    except Exception as e:
        logger.error(f"Error fetching bet details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/bets/cashout")
def cashout_bet(ticket_id: str, total_cashout: float = 0):
    try:
        sdk_client = get_client()
        result = sdk_client.cashout(ticket_id=ticket_id, total_cashout=total_cashout)
        return result
    except Exception as e:
        logger.error(f"Error executing cashout: {e}")
        raise HTTPException(status_code=500, detail=str(e))
