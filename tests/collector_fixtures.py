"""Exclusivement fictif ; mêmes volumes que la recette, sans export personnel."""
from uuid import UUID

STAMP="2026-11-15T12:00:00.000Z"


def export_fixture(projects=3,threads=4):
    result={"source":"mon-gpt-collector","schemaVersion":2,"exportedAt":STAMP,"projects":[],"conversations":[]}
    for i in range(projects):
        key=f"g-p-{i+1:032x}"
        title="Développement" if i<2 else ("Atelier solaire" if i==2 else f"Projet imaginaire {i+1:02}")
        result["projects"].append(dict(projectKey=key,observedName=title,firstSeenAt=STAMP,lastSeenAt=STAMP,seenCount=1,nameObservedAt=STAMP,evidence={"kind":"direct-control","url":None}))
    titles=["Un jardin sur la Lune","Le carnet des couleurs","Un café parmi les étoiles","Voyage en papier"]
    for i in range(threads):
        identity=str(UUID(int=i+1))
        key=result["projects"][i%projects]["projectKey"] if projects and i<(56 if threads>=115 else threads-1) else None
        url=f"https://chatgpt.com/g/{key}/c/{identity}" if key else f"https://chatgpt.com/c/{identity}"
        result["conversations"].append(dict(conversationId=identity,url=url,observedTitle=titles[i%4]+(f" · étude {i+1:03}" if i>=4 else ""),firstSeenAt=STAMP,lastSeenAt=STAMP,seenCount=1,observedUrls=[url],observedProjectKeys=[key] if key else [],lastObservedActive=False))
    return result
