# MG-008b — Audit du DOM connecté, anonymisé

15 novembre 2026, CODEX-VM. **Le DOM de la session Chrome déjà authentifiée préparée par David a réellement été examiné avant modification du scanner.** Aucun nouveau profil non connecté utilisé comme substitut à cet audit. Les valeurs ci-dessous sont remplacées par des noms et clés fictifs ; aucun nom, UUID, export personnel ou capture de la session n’est enregistré dans ces livrables.

## Faits constatés avant code

Deux projets réels distincts ont été examinés dans la navigation : A développé, B d’abord replié, puis développé manuellement. Leurs clés sont différentes. Pour chacun, le libellé sémantique du contrôle est égal au texte affiché dans son propre élément de titre. Les contrôles ont été isolés dans Elements ; leur HTML de navigation a été lu uniquement en mémoire, sans dump de page ou de profil.

Le contrôle natif est un **`div[role="button"]`**, avec :

```html
<div data-sidebar-project-kind="local"
     data-sidebar-project-container-id="project:g-p-11111111111111111111111111111111">
  <!-- Quelques wrappers de présentation sans rôle dans l’identification. -->
  <div role="button" tabindex="0"
       data-app-action-sidebar-project-row
       data-app-action-sidebar-project-id="g-p-11111111111111111111111111111111"
       data-app-action-sidebar-project-label="Projet A"
       data-app-action-sidebar-project-collapsed="false"
       aria-expanded="true" aria-labelledby="project-a-label">
    <span id="project-a-label">
      <span data-marquee-content="true">Projet A</span>
    </span>
    <!-- Actions secondaires de projet, séparées du titre propre. -->
  </div>
  <div aria-hidden="false">
    <!-- Liste des liens de fils du projet, séparée du contrôle nommé. -->
  </div>
</div>
```

Extrait **réduit et anonymisé**, wrappers inutiles et classes supprimés. Les attributs et leur relation proviennent du vrai DOM, pas d’une structure imaginée pour les tests. Le contrôle nommé ne contient **aucun lien de conversation**. Le propriétaire `data-sidebar-project-container-id="project:…"` porte la même clé ; les projets voisins ont leur propre propriétaire. Les éléments de liste sont des `div[role="listitem"]`, pas nécessairement des `li`.

Sur B replié, les mêmes attributs clé/libellé existent, `aria-expanded="false"` et `data-app-action-sidebar-project-collapsed="true"` ; le contenu enfant est inerte/caché. Après clic manuel, `aria-expanded` devient vrai, le marqueur collapsed devient faux, les liens enfants apparaissent, **la clé et le libellé du contrôle restent identiques**. Aucun besoin de deviner le nom à partir des fils.

L’accueil de B a été ouvert uniquement par **Page d’accueil du projet** dans son menu. Son URL `/g/CLÉ/project` concorde avec le contrôle. L’accueil affiche aussi des aperçus de messages : retour à l’accueil général et détachement de DevTools pour poursuivre l’inspection sans capturer ces aperçus. Aucun de ces écrans personnels n’est conservé ou publié.

## Cause racine de MG-008a

1. Le scanner direct ne cherche que `data-project-id` / `data-project-key`. Ces attributs **ne sont pas présents** sur les contrôles réels examinés. La clé est dans **`data-app-action-sidebar-project-id`**, le nom dans **`data-app-action-sidebar-project-label`**.
2. Le fallback développé cherche `button[aria-expanded]` ou un treeitem. Le vrai contrôle est un **div de rôle button**. Il n’est donc pas candidat à ce fallback, malgré son `aria-expanded` réel.
3. Les liens de fils sont dans un contenu voisin du contrôle, sous le même propriétaire. Les anciennes hypothèses de liens contenus dans le bouton ou de relation `aria-controls` réciproque ne correspondent pas à ces deux cas.
4. `projectName` ne reçoit jamais ces contrôles dans le chemin direct. Pour A/B, le problème se situe donc **avant** le traitement du nom ; le titre propre observé concorde avec le libellé sémantique. Les classes de marquee ne doivent pas devenir des sélecteurs.

Le fallback des conversations reconnaît néanmoins les vrais href `/g/g-p-…/c/UUID`, d’où les clés connues avec `key-only`. Cela explique l’écart observé sans accuser à tort le stockage ou la fusion par clé.

## Réparation fondée sur ces preuves

Ajouter le contrôle natif à l’adaptateur, vérifier sa clé et son propriétaire exact, puis vérifier que le libellé sémantique concorde avec le titre propre visible/accessiblement nommé **dans ce même contrôle**. Conserver `evidence.kind="direct-control"`, le schéma v2, les trois modes et la fusion existante. Aucun rapprochement par voisin, index, classe générée, titre de fil ou libellé homonyme.

Observer les mutations de ces attributs et de leur titre afin que le même mécanisme fonctionne en Auto large et après changement SPA. Une clé invalide, un propriétaire contradictoire, un titre absent ou en désaccord doivent laisser le nom inconnu. Des mots génériques ou d’action peuvent être de vrais noms : seule la preuve directe concordante permet de les accepter sans découpage arbitraire.

## Accès et confidentialité

Le contrôle natif a nécessité des captures de travail non sauvegardées ; **aucune capture personnelle n’est publiée**. Seuls les contrôles de navigation, leurs titres/attributs et les URL de projet ont servi à l’audit. Aucun cookie, token, profil, API interne ou stockage ChatGPT lu. Le collage en console est bloqué par la protection self-XSS de Chrome ; prise en main demandée à David, sans contournement. L’inspection Elements continue indépendamment de ce blocage. La recette corrigée et son statut final sont détaillés dans le rapport.
