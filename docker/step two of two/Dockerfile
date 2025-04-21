# from basemachine to finalmachine

FROM ds-ia-base-machine-amd64:dev

COPY api/r2d2.h5 api/r2d2.h5
COPY api/murphy_final.keras api/murphy_final.keras
COPY api/chewbacca.keras api/chewbacca.keras
COPY api/preproc_basic.pkl api/preproc_basic.pkl
COPY api/mf.pkl api/mf.pkl

COPY api/app.py api/app.py

CMD uvicorn api.app:app --host 0.0.0.0 --port $PORT
