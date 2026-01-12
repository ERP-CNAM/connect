# CONNECT

## Principe

Bus de communication sur l'ERP distribué.

Connect transmet les requêtes entre les différents services (modules) de l'ERP avec une gestion des autorisations et le logging des événements.

### Utilisation

Les services pouvant être appelés doivent s'enregistrer auprès de Connect et lister les routes et autorisations nécessaires.

Les services appelants peuvent formuler des appels vers les services enregistrés à l'aide d'une structure standard à Connect. La structure du payload de données est à coordonner avec le service demandé.

## Structures de communication

### Ping Connect

Connect `/ping` **GET**

Renvoie le statut HTTP 200 lorsque tout fonctionne bien.

### Enregistrement d'un service

Connect `/register` **POST**

Les services sont conservés en mémoire par instance de Connect.

Le chemin de la route supporte la notation wildcard sous la forme `{element}` en faisant usage des accolades.

```json
{
  "name": "string", // Nom du service
  "description": "string",
  "version": "string",
  "routes": [
    {
      "path": "string", // Chemin de la route
      "method": "string", // GET, POST, PUT, PATCH, DELETE, OPTIONS, HEAD, TRACE
      "permission": 0 // Bitmask pour le contrôle d'accès (0 = route publique)
    }
  ],
  "overrideIp": "string", // Optionnel. Utiliser une autre adresse IP. Pour Docker : host.docker.internal
  "listeningPort": 0, // Port d'écoute du service (l'IP est déterminée automatiquement)
  "apiKey": "string" // Clé de l'API Connect pour permettre l'enregistrement du service
}
```

### Catalogue des services

Connect `/services` **GET**

```json
[
  {
    "name": "string",
    "description": "string",
    "version": "string",
    "routes": [
      {
        "path": "string",
        "method": "string",
        "permission": 0
      }
    ]
  }
]
```

### Échange de données

Connect `/connect`

Selon la route appelée, utiliser la méthode HTTP correspondante sur la route `/connect` (**GET**, **POST**, **PUT**, **PATCH**, **DELETE**, **OPTIONS**, **HEAD**, **TRACE**).

#### Envoyé par le client

Si applicable, la requête doit contenir le JWT à des fins d'authentification. Soit dans le champ "Authorization" de l'en-tête soit dans les cookies de la requête (clé "token").

Si un service effectue la requête, il peut remplir le champ "apiKey" pour passer la vérification d'accès utilisateur.

```json
{
  "apiKey": "string", // Optionnel. Clé de l'API Connect pour permettre l'accès direct à toutes les routes (seulement si service)
  "clientName": "string", // Nom du module appelant
  "clientVersion": "string", // Version du module appelant
  "serviceName": "string", // Nom (name) du service enregistré à appeler
  "path": "string", // Chemin de la route du service
  "debug": false, // Pour faciliter certains tests
  "payload": null // Données. Contenu de la requête. JSON au format libre
}
```

#### Envoyé au service

La requête n'est émise que si l'accès est possible et autorisé (vérification de la route (+ méthode HTTP), validation du JWT et application du bitmask sur le code permission de la route).

L'appel est fait sur le service avec `[IP]`:`listeningPort`/`path` avec la méthode HTTP utilisée à l'appel.

La clé API de Connect est envoyée dans chaque requête pour permettre aux services d'authentifier Connect. Le service possède déjà la clé API, car il l'a transmise plus tôt pour s'enregistrer.

```json
{
  "apiKey": "string", // Clé de l'API Connect pour permettre au service d'authentifier l'émetteur de l'appel
  "debug": false, // Pour faciliter certains tests
  "userData": {}, // Informations du JWT décodées, rien dans l'objet si non authentifié
  "payload": null // Données. Contenu de la requête. JSON au format libre
}
```

#### Reçu par connect (du service)

Le code HTTP de la requête doit être défini en accord avec le résultat.

```json
{
  "success": true, // Le traitement a réussi, sinon envoi d'une erreur au client
  "message": "string", // À titre informatif ou en cas d'erreur
  "payload": null // Données. Résultat de la requête. JSON au format libre
}
```

#### Renvoyé au client (résultat final)

Le code HTTP de la requête est répliqué du service (sauf si erreur interne Connect).

Le log est enregistré avant renvoi des informations au client.

```json
{
  "success": true,
  "id": 0, // Généré par Connect, id de la requête (pour retrouver le log)
  "status": "string", // success, error (erreur du service), unregistered (le service ou la route appelée n'existe pas), unreachable (le service appelé ne répond pas), unauthorized (permissions insuffisantes), connect_error (erreur interne à Connect)
  "message": "string", // À titre informatif ou en cas d'erreur
  "payload": null // Données. Résultat de la requête. JSON au format libre
}
```

## Données loggées

Description d'une ligne de log.

```json
{
  "id": 0,
  "timestampIn": 0, // Généré par Connect, dès réception (POSIX ms)
  "timestampOut": 0, // Généré par Connect, à l'envoi retour (POSIX ms)
  "identification": {
    "connectVersion": "string",
    "clientName": "string",
    "clientVersion": "string",
    "serviceName": "string",
    "serviceVersion": "string"
  },
  "request": {
    "success": true,
    "path": "string",
    "method": "string", // Méthode HTTP utilisée
    "httpCode": 0, // Code HTTP retour de la requête
    "status": "string",
    "message": "string"
  },
  "data": {
    "debug": false,
    "userData": {},
    "payloadIn": null, // Données en entrée
    "payloadOut": null // Données en sortie
  }
}
```

## Authentification

Informations contenues dans le JWT (algorithme HS256) pour le champ `userData` :

```json
{
  "exp": 0, // Date d'expiration du JWT (POSIX sec)
  "userId": "string",
  "permission": 0 // Bitmask de permission pour l'accès aux routes des services
}
```
