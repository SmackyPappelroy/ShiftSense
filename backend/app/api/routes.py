from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.models import Workspace, User, Finding
from app.schemas.common import WorkspaceCreate, WorkspaceOut, FindingOut
from app.schemas.auth import Token, UserCreate
from app.utils.security import hash_password, verify_password, create_access_token
from app.services.importers import import_csv_timeseries, import_plc_text, import_sql_table
from app.analytics.engine import analyze_timeseries, analyze_plc_code
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/auth/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.email)
    return Token(access_token=token)


@router.post("/auth/users", response_model=Token)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(email=payload.email, password_hash=hash_password(payload.password), role=payload.role)
    db.add(user)
    db.commit()
    token = create_access_token(user.email)
    return Token(access_token=token)


@router.post("/workspaces", response_model=WorkspaceOut)
def create_workspace(payload: WorkspaceCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    workspace = Workspace(name=payload.name, customer=payload.customer, site=payload.site)
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


@router.get("/workspaces", response_model=list[WorkspaceOut])
def list_workspaces(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Workspace).all()


@router.post("/imports/csv/{workspace_id}")
def upload_csv(workspace_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    content = file.file.read().decode("utf-8")
    dataset, _ = import_csv_timeseries(db, workspace_id, content)
    findings = analyze_timeseries(db, dataset)
    return {"dataset_id": dataset.id, "findings": [f.id for f in findings]}


@router.post("/imports/plc/{workspace_id}")
def upload_plc(workspace_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    content = file.file.read().decode("utf-8")
    dataset = import_plc_text(db, workspace_id, file.filename, content, language="st")
    findings = analyze_plc_code(db, dataset)
    return {"dataset_id": dataset.id, "findings": [f.id for f in findings]}


@router.post("/imports/sql/{workspace_id}")
def import_sql(
    workspace_id: int,
    connection_url: str,
    table: str,
    ts_column: str,
    tag_column: str,
    value_column: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    dataset, count = import_sql_table(db, workspace_id, connection_url, table, ts_column, tag_column, value_column)
    findings = analyze_timeseries(db, dataset)
    return {"dataset_id": dataset.id, "rows": count, "findings": [f.id for f in findings]}


@router.get("/findings/{dataset_id}", response_model=list[FindingOut])
def list_findings(dataset_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Finding).filter(Finding.dataset_id == dataset_id).all()
