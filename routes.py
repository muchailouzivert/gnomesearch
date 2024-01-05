from typing import Optional
from fastapi import FastAPI, Request, Header, Depends, status, HTTPException, responses
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pathlib import Path
from database import engine, get_db
from models import Films
from datetime import datetime
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).parent.parent.absolute() / "kyrsova"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


@app.get('/index', response_class=HTMLResponse)
async def movie_list(
    request: Request,
    hx_request: Optional[str] = Header(None),
    db: Session = Depends(get_db),
    page: int = 1
):
    nm = 3
    OFFSET = (page - 1) * nm
    films = db.query(models.Films).offset(OFFSET).limit(nm).all()
    context = {"request": request, "films": films, "page": page}
    if hx_request:
        return templates.TemplateResponse("table.html", context)
    return templates.TemplateResponse("index.html", context)

@app.get("/movies")
async def movies(
    request: Request,
    db: Session = Depends(get_db)
):
    films = db.query(models.Films).all()
    context = {"request": request, "films": films}
    return templates.TemplateResponse("movies.html", context)

@app.get("/search")
def search_movies(request: Request, 
                  query: Optional[str] = None,
                  db: Session = Depends(get_db),
):
    if query is not None:
        films = db.query(Films).filter(Films.name.contains(query)).all()
        context = {"request": request, "films": films}
        return templates.TemplateResponse("search.html", context)

    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/detail/{name}")
def film_detail(request: Request, name: str, db: Session = Depends(get_db)):
    film = db.query(Films).filter(Films.name == name).first()
    return templates.TemplateResponse(
        "movie_detail.html", {"request": request, "film": film}
    )

@app.get("/add_movie")
def add_movie(request:Request):
    return templates.TemplateResponse("add_movie.html", {"request": request})

@app.post("/add_movie")
async def add_movie(request: Request, db: Session = Depends(get_db)):
    form = await request.form()

    name = form.get('name')
    director = form.get('director')
    startYear_str = form.get('startYear')
    category = form.get('category')
    runtimeMinutes = form.get('runtimeMinutes')
    rate = form.get('rate')
    description = form.get('description')
    image = form.get('image')

    startYear = datetime.strptime(startYear_str, '%Y-%m-%d').date() if startYear_str else None

    film = Films(name=name, director=director, startYear=startYear, category=category, runtimeMinutes=runtimeMinutes, rate=rate, description=description, image=image)
    db.add(film)
    db.commit()
    db.refresh(film)
    return responses.RedirectResponse(f"/detail/{film.name}", status_code=status.HTTP_302_FOUND)

@app.get("/delete_movie")
def show_movie_to_delete(request: Request, db: Session = Depends(get_db)):
    existing_movie = db.query(models.Films).all()
    return templates.TemplateResponse("edit_movie.html", {"request": request, "films": existing_movie})

@app.delete("/delete_movie")
async def delete_movie(name: str, db: Session = Depends(get_db)):
    existing_movie = db.query(Films).filter(Films.name == name).first()
    
    if existing_movie:
        db.delete(existing_movie)
        db.commit()
        return {"message": "Movie deleted successfully"}
        
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Movie with name '{name}' not found"
        )

@app.get("/update_movie/{name}")
async def update_movie_get(name: str, request: Request, db: Session = Depends(get_db)):
    existing_movie = db.query(models.Films).filter(models.Films.name == name).first()

    if existing_movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with name '{name}' not found")

    return templates.TemplateResponse("update_movie.html", {'request': request, "film": existing_movie})

@app.post("/update_movie/{name}")
async def update_movie_post(name: str, request: Request, db: Session = Depends(get_db)):
    existing_movie = db.query(models.Films).filter(models.Films.name == name).first()

    if existing_movie is None:
        raise HTTPException(status_code=404, detail=f"Movie with name '{name}' not found")

    form = await request.form()

    director = form.get('director')
    startYear_str = form.get('startYear')
    category = form.get('category')
    runtimeMinutes = form.get('runtimeMinutes')
    rate = form.get('rate')
    description = form.get('description')
    image = form.get('image')

    startYear = datetime.strptime(startYear_str, '%Y-%m-%d').date() if startYear_str else None

    existing_movie.director = director
    existing_movie.startYear = startYear
    existing_movie.category = category
    existing_movie.runtimeMinutes = runtimeMinutes
    existing_movie.rate = rate
    existing_movie.description = description
    existing_movie.image = image

    db.commit()

    return responses.RedirectResponse(f"/detail/{existing_movie.name}", status_code=status.HTTP_302_FOUND)

