chemin_fichier = "teaching_akg.ttl"

from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
from rdflib.namespace import CSVW, DC, DCAT, DCTERMS, DOAP, FOAF, ODRL2, ORG, OWL
from rdflib import Graph, URIRef, Literal, BNode
from rdflib.namespace import FOAF, RDF

# Load the RDF data
graph = Graph()

graph.parse("teaching_akg.ttl", format="ttl")

# Define namespace and type for entities (adjust as needed)
TAO = Namespace("http://sonfack.com/2024/01/tao#")  # Replace with your actual namespace

# Extract and print relevant assertions
relevant_assertions = []

for subj, pred, obj in graph:
    # Exclude subjects and predicates starting with "has" or "is"
    if not str(pred).startswith("http://sonfack.com/2024/01/tao#has") and not str(pred).startswith("http://sonfack.com/2024/01/tao#is"):
        relevant_assertions.append((subj, pred, obj))

# Print relevant assertions
for subj, pred, obj in relevant_assertions:
    print(f"Subject: {subj.split('#')[-1]}\nPredicate: {pred.split('#')[-1]}\nObject: {obj.split('#')[-1]}\n" )

import networkx as nx
import matplotlib.pyplot as plt

akg_file = "teaching_akg.ttl"
g = Graph()
g.parse(akg_file)
G = nx.DiGraph()
akg_namespace = Namespace("http://sonfack.com/2023/12/tao/")
cao_namespace = Namespace("http://sonfack.com/2023/12/cao/")


def read_all_activities(akg: Graph, as_str=True) -> list:
    """This function returns all activities of an activity knowledge graph
    - akg: an activity knowledge graph as parsed by RDFLib
    - as_str: (boolean) tells if the activities are simple str default = True
    """
    activities_list = [str(activity) if as_str else activity for activity in akg.subjects(predicate=RDF.type, object=cao_namespace.Activity, unique=True)]
    return activities_list


def read_akg_node(node_uri: str, akg:Graph, as_str=True) -> dict:
    """This function returns all elements directly linked to a akg node
    - activity_uri (string): the given activity uri in graph akg
    - akg (Graph): an activity knowledge graph as parsed by RDFLib
    """
    activity_info = {}
    activity_uri_ref = f"{akg_namespace}{node_uri}"
    print(activity_uri_ref)
    for act_predicate, act_object in akg.predicate_objects(subject=URIRef(activity_uri_ref)):
        pred = act_predicate
        obj = act_object
        if as_str:
            pred = str(act_predicate)
            obj = str(act_object)
        if pred in activity_info:
            existing_objects = activity_info[pred] + [obj]
            activity_info[pred] = existing_objects
        else:
            activity_info[pred] = [obj]
    return activity_info

def add_activity_to_nxgraph(G, activity_uri, activity_info):
    #print("ajout de l'activité", activity_uri)
    #print("affichage des informations", activity_info)
    activity_g = nx.DiGraph()

    for pred, obj_list in activity_info.items():
        pred_label = pred.split('/')[-1]
        if '#' in pred_label:
            pred_label = pred_label.split('#')[1]

        for obj in obj_list:
            obj_label = obj.split('/')[-1]
            node_info = read_akg_node(obj_label, g)

            if node_info:
                # Assurez-vous que vous récupérez une chaîne et non une liste
                obj_label = node_info.get('http://sonfack.com/2023/12/tao/hasName', [None])[0]
                if obj_label is None:
                    continue  # Passer à l'itération suivante si obj_label est None


            G.add_node(activity_uri)
            G.add_node(obj_label)
            G.add_edge(activity_uri, obj_label, label=pred_label)
            activity_g.add_node(activity_uri)
            activity_g.add_node(obj_label)
            activity_g.add_edge(activity_uri, obj_label, label=pred_label)

    visualize_activity(activity_g)

def visualize_activity(G):
    # Visualize the graph
    plt.figure(figsize=(12, 12))

    # Generate positions for nodes using a layout algorithm
    pos = nx.spring_layout(G, seed=42)

    # Draw the nodes and edges
    nx.draw(G, pos, with_labels=True, node_size=300, node_color="blue", font_size=5, font_weight="bold", edge_color="black")

    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

    # Show plot
    plt.title("Graphe de Connaissances des Activités")
    plt.show()

liste_activity = read_all_activities(g, as_str=True)
print(liste_activity)
for activity in liste_activity:
    subj = activity.split('/')[-1]
    info_activity = read_akg_node(subj, g, as_str=True)
    print(info_activity)
    add_activity_to_nxgraph(G,activity,info_activity)


# Visualize the graph
plt.figure(figsize=(12, 12))

# Generate positions for nodes using a layout algorithm
pos = nx.spring_layout(G, seed=42)

# Draw the nodes and edges
nx.draw(G, pos, with_labels=True, node_size=300, node_color="blue", font_size=5, font_weight="bold", edge_color="black")

# Draw edge labels
edge_labels = nx.get_edge_attributes(G, 'label')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red', font_size=8)

# Show plot
plt.title("Graphe de Connaissances des Activités")
plt.show()


#g = Graph()

# Remplacer par le chemin de votre fichier TTL local
#ttl_file_path = "C:\\Users\\LENOVO\\OneDrive\\Documents\\TPE\\teaching_akg.ttl"

# Parser le fichier RDF au format Turtle
#g.parse(ttl_file_path, format="ttl")

# ----- Définir les namespaces cao et tao -----
cao = Namespace("http://sonfack.com/2023/12/cao/")
tao = Namespace("http://sonfack.com/2023/12/tao/")

# ----- Requête SPARQL mise à jour pour regrouper les types de ressources -----
query_grouped_resources = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX cao: <http://sonfack.com/2023/12/cao/>
PREFIX tao: <http://sonfack.com/2023/12/tao/>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?resource ?resourceType
WHERE {
    ?resource rdf:type ?resourceType .

    # Exclure les ressources de type ontologique et autres propriétés non pertinentes
    FILTER NOT EXISTS { ?resource rdf:type owl:Ontology }
    FILTER NOT EXISTS { ?resource rdf:type owl:Class }
    FILTER NOT EXISTS { ?resource rdf:type owl:ObjectProperty }
    FILTER NOT EXISTS { ?resource rdf:type owl:TransitiveProperty }

    # Grouper les ressources par type de catégorie

    # Activités
    { ?resource rdf:type cao:Activity }
    UNION
    { ?resource rdf:type cao:Action }

    # Ressources matérielles
    UNION
    { ?resource rdf:type tao:Laptop }
    UNION
    { ?resource rdf:type tao:Desktop }
    UNION
    { ?resource rdf:type tao:HardDocument }
    UNION
    { ?resource rdf:type tao:Projector }

    # Ressources immatérielles
    UNION
    { ?resource rdf:type tao:DigitalResource }
    UNION
    { ?resource rdf:type tao:Video }
    UNION
    { ?resource rdf:type tao:SoftDocument }

    # Ressources humaines
    UNION
    { ?resource rdf:type tao:Teacher }
    UNION
    { ?resource rdf:type tao:Tutor }
    UNION
    { ?resource rdf:type tao:Students }

    # Ressources physiques
    UNION
    { ?resource rdf:type tao:ClassRoom }
    UNION
    { ?resource rdf:type tao:PracticalRoom }
    UNION
    { ?resource rdf:type tao:TutorialRoom }
}
"""

# Exécuter la requête SPARQL
results_grouped_resources = g.query(query_grouped_resources)

# Initialiser des listes distinctes pour chaque catégorie
activities = []
hard_resources = []
soft_resources = []
human_resources = []
physical_resources = []

# Organiser les ressources extraites dans les bonnes catégories
for row in results_grouped_resources:
    resource = row['resource']
    resource_type = row['resourceType']

    # Identifier et ajouter les ressources dans les bonnes listes
    if resource_type in [cao.Activity, cao.Action]:
        activities.append(resource)
    elif resource_type in [tao.Laptop, tao.Desktop, tao.HardDocument, tao.Projector]:
        hard_resources.append(resource)
    elif resource_type in [tao.DigitalResource, tao.Video, tao.SoftDocument]:
        soft_resources.append(resource)
    elif resource_type in [tao.Teacher, tao.Tutor, tao.Students]:
        human_resources.append(resource)
    elif resource_type in [tao.ClassRoom, tao.PracticalRoom, tao.TutorialRoom]:
        physical_resources.append(resource)

# Afficher les groupes de ressources extraits
print("Activités :")
for activity in activities:
    print(f"  - {activity}")

print("\nRessources matérielles :")
for hr in hard_resources:
    print(f"  - {hr}")

print("\nRessources immatérielles :")
for sr in soft_resources:
    print(f"  - {sr}")

print("\nRessources humaines :")
for hr in human_resources:
    print(f"  - {hr}")

print("\nRessources physiques :")
for pr in physical_resources:
    print(f"  - {pr}")

from pyvis.network import Network
from IPython.core.display import display, HTML

# Fonction pour organiser les ressources selon leurs types
def organize_resources_by_type(resources):
    resource_groups = {}

    for resource, resource_type in resources:
        if resource_type not in resource_groups:
            resource_groups[resource_type] = []
        resource_groups[resource_type].append(resource)

    return resource_groups

# Fonction pour créer le réseau PyVis avec la taille des nœuds variant selon le nombre de ressources dans chaque groupe
def visualize_resource_graph(resources):
    # Organiser les ressources par type
    resource_groups = organize_resources_by_type(resources)

    # Couleurs par type de ressource (modifiable selon les besoins)
    node_colors = {
        "Activités": "lightblue",
        "Ressources matérielles": "lightcoral",
        "Ressources immatérielles": "green",
        "Ressources humaines": "yellow",
        "Ressources physiques": "lightgray"
    }

    # Créer le réseau PyVis
    net = Network(notebook=True, cdn_resources='in_line', height="750px", width="100%")

    # Ajouter les nœuds avec des tailles basées sur le nombre de ressources
    for group_name, group_resources in resource_groups.items():
        node_size = len(group_resources) * 20 # Taille proportionnelle au nombre de ressources (ajustée)
        net.add_node(group_name, label=group_name, size=node_size, color=node_colors.get(group_name, "lightblue"))

    # Exemple de relations entre groupes (prédicats)
    relations = [
        ("Activités", "Ressources matérielles", "requires"),
        ("Activités", "Ressources immatérielles", "utilizes"),
        ("Activités", "Ressources humaines", "involves"),
        ("Ressources matérielles", "Ressources physiques", "contains"),
        ("Ressources immatérielles", "Ressources humaines", "isUsedBy"),
        ("Ressources humaines", "Ressources physiques", "manages")
    ]

    # Ajouter des arêtes avec des prédicats
    for source, target, predicate in relations:
        net.add_edge(source, target, title=predicate, label=predicate, color="gray", font={'size': 14})

    # Désactiver la physique pour un agencement statique
    net.toggle_physics(False)

    # Sauvegarder et afficher le graphique
    net.show("dynamic_resource_visualization.html")

    # Afficher directement dans Jupyter/Colab
    display(HTML('dynamic_resource_visualization.html'))

    # Ajouter une légende personnalisée
    legend_html = """
    <div style="position: absolute; top: 10px; right: 10px; background: white; padding: 10px; border-radius: 10px; border: 1px solid black;">
        <h4>Légende</h4>
        <p><span style="background-color: lightblue; width: 10px; height: 10px; display: inline-block;"></span> Activités</p>
        <p><span style="background-color: lightcoral; width: 10px; height: 10px; display: inline-block;"></span> Ressources Matérielles</p>
        <p><span style="background-color: green; width: 10px; height: 10px; display: inline-block;"></span> Ressources Immatérielles</p>
        <p><span style="background-color: yellow; width: 10px; height: 10px; display: inline-block;"></span> Ressources Humaines</p>
        <p><span style="background-color: lightgray; width: 10px; height: 10px; display: inline-block;"></span> Ressources Physiques</p>
    </div>
    """

    display(HTML(legend_html))

# Exemple de données de ressources (type, nom)
resources = [
    ("dbcourse-b63a9944-19f6-4f41-bcbd-9333ede86272", "Activités"),
    ("dbtutorial-78aca3f8-53fd-4f47-9406-414b493efe19", "Activités"),
    ("book-b4d784d0-8be6-473f-a4cc-3c5ff8a80b6d", "Ressources matérielles"),
    ("book-5afdf1f7-b15f-450b-be5f-e6e5d0505cb5", "Ressources matérielles"),
    ("software-7b5f05b1-0701-43bb-ad0f-a98a27dc9312", "Ressources immatérielles"),
    ("lecturer-c83b7873-f908-484d-a044-2802814f87d1", "Ressources humaines"),
    ("classroom-b2c326d0-8551-41c4-aee5-11365e117523", "Ressources physiques")
]

# Appeler la fonction de visualisation
visualize_resource_graph(resources)

from pyvis.network import Network
import networkx as nx
from IPython.display import display, HTML

# Fonction pour organiser les ressources selon leurs types
def organize_resources_by_type(resources):
    resource_groups = {}

    for resource, resource_type in resources:
        if resource_type not in resource_groups:
            resource_groups[resource_type] = []
        resource_groups[resource_type].append(resource)

    return resource_groups

# Fonction pour créer le réseau PyVis avec la taille des nœuds variant selon le nombre de ressources dans chaque groupe
def visualize_resource_graph(resources):
    # Organiser les ressources par type
    resource_groups = organize_resources_by_type(resources)
    return resource_groups

# Définir les couleurs pour chaque groupe
node_colors = {
    "Activités": "lightblue",
    "Ressources matérielles": "lightcoral",
    "Ressources immatérielles": "green",
    "Ressources humaines": "yellow",
    "Ressources physiques": "lightgray"
}

# Définir les relations prédéfinies
relations = [
    ("Activités", "Ressources matérielles", "requires"),
    ("Activités", "Ressources immatérielles", "utilizes"),
    ("Activités", "Ressources humaines", "involves"),
    ("Ressources matérielles", "Ressources physiques", "contains"),
    ("Ressources immatérielles", "Ressources humaines", "isUsedBy"),
    ("Ressources humaines", "Ressources physiques", "manages")
]

# Fonction pour afficher les relations pour les nœuds sélectionnés
def visualize_selected_resources(selected_groups, include_actor, resource_groups):
    # Créer le réseau PyVis avec la physique activée
    net_dynamic = Network(notebook=True, cdn_resources='in_line')

    # Ajouter les nœuds et arêtes en fonction de la sélection de l'utilisateur
    for group_name in selected_groups:
        if group_name in resource_groups:
            resources = resource_groups[group_name]
            size = len(resources) * 10  # Taille en fonction du nombre de ressources dans chaque groupe
            net_dynamic.add_node(group_name, label=group_name, size=size, color=node_colors[group_name])

            # Ajouter les relations avec l'acteur principal
            for relation in relations:
                if relation[0] == include_actor and relation[1] == group_name:
                    net_dynamic.add_edge(relation[0], relation[1], title=relation[2], label=relation[2], font={'size': 14, 'color': 'black'}, color='gray')
                elif relation[1] == include_actor and relation[0] == group_name:
                    net_dynamic.add_edge(relation[0], relation[1], title=relation[2], label=relation[2], font={'size': 14, 'color': 'black'}, color='gray')

    # Activer la physique pour un graphe dynamique
    net_dynamic.toggle_physics(False)

    # Générer et afficher le graphe
    net_dynamic.show("dynamic_selected_resources_graph.html")
    display(HTML("dynamic_selected_resources_graph.html"))

# Fonction pour demander la sélection de l'utilisateur
def user_selection():
    print("Veuillez sélectionner les groupes de ressources à afficher (exemple : 1 3 5):")
    print("1. Activités")
    print("2. Ressources matérielles")
    print("3. Ressources immatérielles")
    print("4. Ressources humaines")
    print("5. Ressources physiques")

    # Demander la saisie de l'utilisateur
    selection = input("Entrez les numéros correspondants aux groupes à visualiser (séparés par espace) : ")

    # Mapper la sélection aux groupes
    group_map = {
        "1": "Activités",
        "2": "Ressources matérielles",
        "3": "Ressources immatérielles",
        "4": "Ressources humaines",
        "5": "Ressources physiques"
    }

    selected_groups = [group_map[num] for num in selection.split() if num in group_map]

    # Toujours inclure l'acteur principal (par exemple "Activités")
    include_actor = "Activités"  # Vous pouvez ajuster l'acteur principal ici

    if selected_groups:
        # Générer les groupes de ressources
        resources = [
            ("dbcourse-b63a9944-19f6-4f41-bcbd-9333ede86272", "Activités"),
            ("dbtutorial-78aca3f8-53fd-4f47-9406-414b493efe19", "Activités"),
            ("book-b4d784d0-8be6-473f-a4cc-3c5ff8a80b6d", "Ressources matérielles"),
            ("book-5afdf1f7-b15f-450b-be5f-e6e5d0505cb5", "Ressources matérielles"),
            ("software-7b5f05b1-0701-43bb-ad0f-a98a27dc9312", "Ressources immatérielles"),
            ("lecturer-c83b7873-f908-484d-a044-2802814f87d1", "Ressources humaines"),
            ("classroom-b2c326d0-8551-41c4-aee5-11365e117523", "Ressources physiques")
        ]
        resource_groups = visualize_resource_graph(resources)

        # Afficher la visualisation avec les groupes sélectionnés
        visualize_selected_resources(selected_groups, include_actor, resource_groups)
    else:
        print("Sélection non valide. Veuillez réessayer.")

# Lancer la sélection utilisateur et visualiser les nœuds correspondants
#user_selection()

"""{
  "prefixes": {
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "cao": "http://sonfack.com/2023/12/cao/",
    "tao": "http://sonfack.com/2023/12/tao/",
    "owl": "http://www.w3.org/2002/07/owl#"
  },
  "select": ["?resource", "?resourceType"],
  "distinct": True,  # Correction ici
  "where": [
    {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "?resourceType"},
    {"type": "filter_not_exists", "triple": {"subject": "?resource", "predicate": "rdf:type", "object": "owl:Ontology"}},
    {"type": "filter_not_exists", "triple": {"subject": "?resource", "predicate": "rdf:type", "object": "owl:Class"}},
    {"type": "filter_not_exists", "triple": {"subject": "?resource", "predicate": "rdf:type", "object": "owl:ObjectProperty"}},
    {"type": "filter_not_exists", "triple": {"subject": "?resource", "predicate": "rdf:type", "object": "owl:TransitiveProperty"}},
    {
      "type": "union",
      "queries": [
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "cao:Activity"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "cao:Action"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Laptop"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Desktop"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:HardDocument"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Projector"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:DigitalResource"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Video"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:SoftDocument"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Teacher"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Tutor"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:Students"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:ClassRoom"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:PracticalRoom"},
        {"type": "triple", "subject": "?resource", "predicate": "rdf:type", "object": "tao:TutorialRoom"}
      ]
    }
  ]
}"""