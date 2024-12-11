import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import networkx as nx
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

# Initialiser l'application Dash
app = dash.Dash(__name__)


cao = Namespace("http://sonfack.com/2023/12/cao/")
tao = Namespace("http://sonfack.com/2023/12/tao/")

# Initialiser et charger le graph RDF
g = Graph()
g.parse("teaching_akg.ttl", format="ttl")

# Partie ajoutée pour visualiser le graphe de connaissances des activités
akg_file = "teaching_akg.ttl"
g = Graph()
g.parse(akg_file)
G_activities = nx.DiGraph()
akg_namespace = Namespace("http://sonfack.com/2023/12/tao/")
cao_namespace = Namespace("http://sonfack.com/2023/12/cao/")

def read_all_activities(akg: Graph, as_str=True) -> list:
    """This function returns all activities of an activity knowledge graph
    - akg: an activity knowledge graph as parsed by RDFLib
    - as_str: (boolean) tells if the activities are simple str default = True
    """
    activities_list = [str(activity) if as_str else activity for activity in akg.subjects(predicate=RDF.type, object=cao_namespace.Activity, unique=True)]
    return activities_list

def read_akg_node(node_uri: str, akg: Graph, as_str=True) -> dict:
    """This function returns all elements directly linked to a akg node
    - activity_uri (string): the given activity uri in graph akg
    - akg (Graph): an activity knowledge graph as parsed by RDFLib
    """
    activity_info = {}
    activity_uri_ref = f"{akg_namespace}{node_uri}"
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
    for pred, obj_list in activity_info.items():
        pred_label = pred.split('/')[-1]
        if '#' in pred_label:
            pred_label = pred_label.split('#')[1]

        for obj in obj_list:
            obj_label = obj.split('/')[-1]
            node_info = read_akg_node(obj_label, g)

            if node_info:
                obj_label = node_info.get('http://sonfack.com/2023/12/tao/hasName', [None])[0]
                if obj_label is None:
                    continue

            G.add_node(activity_uri)
            G.add_node(obj_label)
            G.add_edge(activity_uri, obj_label, label=pred_label)

def create_activity_graph_figure(G):
    pos = nx.spring_layout(G, seed=42)  # Utiliser une disposition Spring pour minimiser le chevauchement
    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, node_text = [], [], []
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node.split('/')[-1])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        hoverinfo='text',
        marker=dict(color='blue', size=15, line=dict(width=3)),  # Augmenter la taille des nœuds et la largeur des bordures
        textposition='top center',
        textfont=dict(size=10)  # Augmenter la taille de la police des étiquettes
    )

    edge_labels = nx.get_edge_attributes(G, 'label')
    edge_annotations = []
    for edge, label in edge_labels.items():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_annotations.append(
            dict(
                x=(x0 + x1) / 2,
                y=(y0 + y1) / 2,
                text=label,
                showarrow=False,
                font=dict(size=10, color='red'),
                xanchor='center',
                yanchor='middle'
            )
        )

    fig = go.Figure(data=[edge_trace, node_trace],
                    layout=go.Layout(title='Graphe de Connaissances des Activités',
                                    titlefont_size=16,
                                    showlegend=False,
                                    hovermode='closest',
                                    margin=dict(b=20, l=5, r=5, t=40),
                                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                    annotations=edge_annotations))
    return fig

# Ajouter les activités au graphe NetworkX
liste_activity = read_all_activities(g, as_str=True)
for activity in liste_activity:
    subj = activity.split('/')[-1]
    info_activity = read_akg_node(subj, g, as_str=True)
    add_activity_to_nxgraph(G_activities, activity, info_activity)

# Créer la visualisation du graphe de connaissances des activités
activity_graph_figure = create_activity_graph_figure(G_activities)

# Définition du layout de l'application
app.layout = html.Div([
    html.H4("Graphe de Connaissances des Activités"),
    dcc.Graph(id='activity-graph', figure=activity_graph_figure),
    html.Hr(),  # Ligne de séparation
    dcc.Dropdown(
        id='resource-type-selector',  # S'assurer que cet ID est utilisé dans un Input
        options=[
            {'label': 'Activités', 'value': 'Activités'},
            {'label': 'Ressources matérielles', 'value': 'Ressources matérielles'},
            {'label': 'Ressources immatérielles', 'value': 'Ressources immatérielles'},
            {'label': 'Ressources humaines', 'value': 'Ressources humaines'},
            {'label': 'Ressources physiques', 'value': 'Ressources physiques'}
        ],
        value=[],
        multi=True,
        placeholder="Sélectionnez les types de ressources à afficher"
    ),
    dcc.Graph(id='network-graph'),  # S'assurer que cet ID est utilisé dans un Output
    html.Div(id='entity-list', style={'marginTop': '20px', 'display': 'flex', 'flexWrap': 'wrap'})  # Ajouter une section pour lister les entités
])

# Définition de la callback existante pour la carte de connaissances
@app.callback(
    [Output('network-graph', 'figure'),
    Output('entity-list', 'children')],
    [Input('resource-type-selector', 'value')]
)
def update_graph(selected_resource_types):
    # Le code original pour mettre à jour la carte de connaissances reste inchangé
    try:
        # Si aucune catégorie n'est sélectionnée, afficher toutes les ressources et leurs relations par défaut
        if not selected_resource_types:
            selected_resource_types = ["Activités", "Ressources matérielles", "Ressources immatérielles", "Ressources humaines", "Ressources physiques"]

        # Requête SPARQL pour regrouper les types de ressources
        query_grouped_resources = """
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX cao: <http://sonfack.com/2023/12/cao/>
            PREFIX tao: <http://sonfack.com/2023/12/tao/>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            SELECT DISTINCT ?resource ?resourceType
            WHERE {
                ?resource rdf:type ?resourceType .
                FILTER NOT EXISTS { ?resource rdf:type owl:Ontology }
                FILTER NOT EXISTS { ?resource rdf:type owl:Class }
                FILTER NOT EXISTS { ?resource rdf:type owl:ObjectProperty }
                FILTER NOT EXISTS { ?resource rdf:type owl:TransitiveProperty }
                { ?resource rdf:type cao:Activity } UNION
                { ?resource rdf:type cao:Action } UNION
                { ?resource rdf:type tao:Laptop } UNION
                { ?resource rdf:type tao:Desktop } UNION
                { ?resource rdf:type tao:HardDocument } UNION
                { ?resource rdf:type tao:Projector } UNION
                { ?resource rdf:type tao:DigitalResource } UNION
                { ?resource rdf:type tao:Video } UNION
                { ?resource rdf:type tao:SoftDocument } UNION
                { ?resource rdf:type tao:Teacher } UNION
                { ?resource rdf:type tao:Tutor } UNION
                { ?resource rdf:type tao:Student } UNION
                { ?resource rdf:type tao:ClassRoom } UNION
                { ?resource rdf:type tao:PracticalRoom } UNION
                { ?resource rdf:type tao:TutorialRoom } UNION
                { ?resource rdf:type tao:BSc }
            }
            """
        results_grouped_resources = g.query(query_grouped_resources)
        groups = {
            "Activités": [],
            "Ressources matérielles": [],
            "Ressources immatérielles": [],
            "Ressources humaines": [],
            "Ressources physiques": []
        }

        for row in results_grouped_resources:
            resource = str(row[0])
            resource_type = str(row[1]).split('#')[-1]
            if "Activity" in resource_type or "Action" in resource_type:
                groups["Activités"].append(resource)
            elif any(x in resource_type for x in ["Laptop", "Desktop", "HardDocument", "Projector"]):
                groups["Ressources matérielles"].append(resource)
            elif any(x in resource_type for x in ["DigitalResource", "Video", "SoftDocument"]):
                groups["Ressources immatérielles"].append(resource)
            elif any(x in resource_type for x in ["Teacher", "Tutor", "Student"]):
                groups["Ressources humaines"].append(resource)
            elif any(x in resource_type for x in ["ClassRoom", "PracticalRoom", "TutorialRoom", "BSc"]):
                groups["Ressources physiques"].append(resource)

        # Déplacer `TutorialRoom` et `BSc` dans Ressources physiques et `Student` dans Ressources humaines
        for resource in groups["Ressources humaines"][:]:
            if any(x in resource.lower() for x in ["tutorialroom", "bsc"]):
                groups["Ressources humaines"].remove(resource)
                groups["Ressources physiques"].append(resource)
        for resource in groups["Ressources physiques"][:]:
            if "student" in resource.lower():
                groups["Ressources physiques"].remove(resource)
                groups["Ressources humaines"].append(resource)

        # Créer un graphe NetworkX
        G = nx.DiGraph()
        # Créer un seul nœud pour chaque type de ressource sélectionné
        for group_name in selected_resource_types:
            G.add_node(group_name, label=group_name, size=len(groups[group_name]) * 10, entities=groups[group_name])  # La taille du nœud dépend du nombre d'entités

        # Ajouter des relations avec des étiquettes entre les groupes sélectionnés
        relations = [
            ("Activités", "Ressources matérielles", "requires"),
            ("Activités", "Ressources immatérielles", "utilizes"),
            ("Activités", "Ressources humaines", "involves"),
            ("Ressources matérielles", "Ressources physiques", "contains"),
            ("Ressources immatérielles", "Ressources humaines", "isUsedBy"),
            ("Ressources humaines", "Ressources physiques", "manages")
        ]
        for source_group, target_group, relation_label in relations:
            if source_group in selected_resource_types and target_group in selected_resource_types:
                G.add_edge(source_group, target_group, label=relation_label)

        # Générer la visualisation avec Plotly
        pos = nx.spring_layout(G, seed=42)  # Utiliser une disposition spring plus fiable
        edge_x, edge_y, edge_annotations = [], [], []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            # Ajouter une annotation pour chaque relation
            edge_annotations.append(
                dict(
                    x=(x0 + x1) / 2,
                    y=(y0 + y1) / 2,
                    text=edge[2]['label'],
                    showarrow=False,
                    font=dict(size=10, color='red'),
                    xanchor='center',
                    yanchor='middle'
                )
            )
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2.5, color='#888'),  # Épaisseur augmentée et couleur contrastée
            hoverinfo='none',
            mode='lines',
            showlegend=False
        )

        node_x, node_y, node_text, node_color, node_size, customdata = [], [], [], [], [], []
        color_map = {"Activités": "lightblue", "Ressources matérielles": "lightcoral", "Ressources immatérielles": "green",
                     "Ressources humaines": "yellow", "Ressources physiques": "lightgray"}
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            group = G.nodes[node]['label']
            node_color.append(color_map[group])
            node_size.append(G.nodes[node]['size'])  # Utiliser la taille du nœud basée sur le nombre d'entités
            node_text.append(f"{group}")
            customdata.append("\n".join([entity.split('/')[-1] for entity in G.nodes[node]['entities']]))  # Ajouter les noms des entités sans UUID

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            text=node_text,
            hoverinfo='text',
            marker=dict(color=node_color, size=node_size, line=dict(width=2)),
            textposition='top center',
            showlegend=False,
            customdata=customdata,  # Ajouter les entités pour l'affichage au survol
            hovertemplate="<b>%{text}</b><br>Entités: %{customdata}<extra></extra>"
        )

        # Ajouter une légende
        legend_traces = []
        for group_name, color in color_map.items():
            legend_traces.append(
                go.Scatter(
                    x=[None], y=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    legendgroup=group_name,
                    showlegend=True,
                    name=group_name
                )
            )

        fig = go.Figure(data=legend_traces + [edge_trace, node_trace],
                        layout=go.Layout(title='Visualisation de la carte de connaissances', titlefont_size=16,
                                         showlegend=True, hovermode='closest', margin=dict(b=20, l=5, r=5, t=40),
                                         xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                         yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                                         annotations=edge_annotations + [
                                             dict(
                                                 xref='paper', yref='paper',
                                                 x=1.05, y=1.05,
                                                 text='<b>Légende</b>',
                                                 showarrow=False,
                                                 font=dict(size=14, color='black'),
                                                 xanchor='left', yanchor='bottom'
                                             )
                                         ],
                                         dragmode='pan',  # Permettre le panoramique
                                         autosize=True,  # Permettre le zoom et le redimensionnement
                                         uirevision='graph'  # Conserver la disposition lors du déplacement des nœuds
                        ))

        # Liste des entités en pied de page
        entity_list = []
        for group_name in selected_resource_types:
            entities = ["-".join(entity.split('/')[-1].split('-')[:2]) for entity in groups[group_name]]
            entity_list.append(html.Div([
                html.H5(f"{group_name} ({len(entities)} entités):"),
                html.Ul([html.Li(entity) for entity in entities])
            ], style={'flex': '1', 'margin': '10px'}))

        return fig, entity_list

    except Exception as e:
        print("Erreur dans update_graph:", e)
        return go.Figure(), []  # Retourne une figure vide et une liste vide en cas d'erreur

if __name__ == '__main__':
    app.run_server(debug=True)
