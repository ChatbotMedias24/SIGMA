import streamlit as st
import openai
import streamlit as st
from dotenv import load_dotenv
import pickle
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms import OpenAI
from langchain.callbacks import get_openai_callback
import os
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from streamlit_chat import message  # Importez la fonction message
import toml
import docx2txt
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
import docx2txt
from dotenv import load_dotenv
if 'previous_question' not in st.session_state:
    st.session_state.previous_question = []

# Chargement de l'API Key depuis les variables d'environnement
load_dotenv(st.secrets["OPENAI_API_KEY"])

# Configuration de l'historique de la conversation
if 'previous_questions' not in st.session_state:
    st.session_state.previous_questions = []

st.markdown(
    """
    <style>

        .user-message {
            text-align: left;
            background-color: #E8F0FF;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: 10px;
            margin-right: -40px;
            color:black;
        }

        .assistant-message {
            text-align: left;
            background-color: #F0F0F0;
            padding: 8px;
            border-radius: 15px 15px 15px 0;
            margin: 4px 0;
            margin-left: -10px;
            margin-right: 10px;
            color:black;
        }

        .message-container {
            display: flex;
            align-items: center;
        }

        .message-avatar {
            font-size: 25px;
            margin-right: 20px;
            flex-shrink: 0; /* Empêcher l'avatar de rétrécir */
            display: inline-block;
            vertical-align: middle;
        }

        .message-content {
            flex-grow: 1; /* Permettre au message de prendre tout l'espace disponible */
            display: inline-block; /* Ajout de cette propriété */
}
        .message-container.user {
            justify-content: flex-end; /* Aligner à gauche pour l'utilisateur */
        }

        .message-container.assistant {
            justify-content: flex-start; /* Aligner à droite pour l'assistant */
        }
        input[type="text"] {
            background-color: #E0E0E0;
        }

        /* Style for placeholder text with bold font */
        input::placeholder {
            color: #555555; /* Gris foncé */
            font-weight: bold; /* Mettre en gras */
        }

        /* Ajouter de l'espace en blanc sous le champ de saisie */
        .input-space {
            height: 20px;
            background-color: white;
        }
    
    </style>
    """,
    unsafe_allow_html=True
)
# Sidebar contents
textcontainer = st.container()
with textcontainer:
    logo_path = "medi.png"
    logoo_path = "NOTEPRESENTATION.png"
    st.sidebar.image(logo_path,width=150)
   
    
st.sidebar.subheader("Suggestions:")
questions = [
    "Donnez-moi un résumé du rapport ",
    "Quels sont les principaux défis financiers identifiés pour les SEGMA dans les secteurs de la santé et de l’éducation ?",        
    "Quels types d'événements génèrent le plus de recettes et sont-ils amenés à se développer dans les prochaines années ?",
    "Quelle est la répartition des ressources des SEGMA entre recettes propres, subventions et excédents reportés ?"
]
# Initialisation de l'historique de la conversation dans `st.session_state`
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = StreamlitChatMessageHistory()
def main():
    text=r"""
    
INTRODUCTION
En tant que services de l’Etat générant des recettes propres, les Services de l'État Gérés
de Manière Autonome (SEGMA) constituent un instrument budgétaire privilégié qui
permet de contribuer efficacement à l’accompagnement et à la mise en oeuvre des
stratégies et des politiques publiques engagées par le gouvernement, et ce, afin
d’améliorer la qualité des prestations offertes aux citoyens.
En effet, les SEGMA jouent un rôle primordial dans la gestion de proximité des services
publics rendus aux usagers, et ce, tout en s’inscrivant dans la dynamique de
modernisation de la gestion publique à travers une optimisation de la programmation et
de l’exécution des dépenses publiques et une meilleure adaptation aux impératifs de la
performance prônée par la loi organique n°13O-13 relative à la loi de finance.
Dans ce cadre, le présent rapport a pour objectif de mettre la lumière sur les principales
réalisations des SEGMA au titre de l’année 2023 et du 1er semestre de l’année 2024, en
comparaison avec celles de 2022, ainsi que leurs plans d’actions au titre de l’année 2025,
tout en les associant, autant que possible, à des objectifs mesurés par des indicateurs
chiffrés, en vue de mettre en évidence le rôle prépondérant que jouent ces SEGMA dans
l’amélioration des services fournis aux citoyens.
Au titre de l’année budgétaire 2024, le nombre des SEGMA s’est établi à 171 services.
Cette année a été donc marquée par l’absence de création de nouveaux SEGMA ou de
suppression de SEGMA existants.
Par ailleurs, il y a lieu de rappeler que les 171 SEGMA inscrits au titre de la loi de finances
2024 sont ventilés selon 8 domaines d’intervention conformément aux grandes
fonctions de l’Etat : le domaine de la santé avec 91 services, le domaine de
l’enseignement, de la formation professionnelle et de la formation des cadres avec 44
services, le domaine de l’équipement, du transport et autres infrastructures économiques
avec 16 services, le domaine des pouvoirs publics et des services généraux avec 9
services, le domaine des activités récréatives qui compte 5 services, le domaine de
l’agriculture et de la pêche maritime comportant deux services, le domaine des autres
actions sociales avec 3 services et le domaine des autres actions économiques avec un
seul service.
Quant aux réalisations financières des SEGMA au titre de l’année 2023, elles se
présentent comme suit :
   Les recettes générées ont atteint les 6.464,50 MDH, dépassant ainsi les prévisions
   qui se situaient autour de 5.055,91 MDH, soit un taux de réalisation de 127,86%. En
   effet, les recettes propres ont enregistré un montant de 2.423,99 MDH avec un taux
   de recouvrement de 176,41%. Les dotations d’équilibre accordées par le Budget de
   l’Etat à certains SEGMA (notamment ceux intervenant dans le domaine de la santé
   et le domaine de l’enseignement, de la formation professionnelle et de la formation
   des cadres, à concurrence de 92,90% du total des allocations) ont atteint un montant
    PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


     de 918,93 MDH. En ce qui concerne l’excédent de recettes sur les paiements à fin
     2022, il a enregistré un montant de 3.121,59 MDH.
► Les meilleures performances en termes de réalisation des recettes propres sont
  enregistrées par les SEGMA intervenant dans le domaine de la santé, et le domaine
  des pouvoirs publics et services généraux, ainsi que par ceux oeuvrant dans le
  domaine de l’équipement, du transport et autres infrastructures économiques. Leurs
  taux de recouvrement respectifs s’élèvent à 197,25%, 196,60% et 168,71%.
► Les dépenses ont franchi les 2.652,31 MDH par rapport à des prévisions chiffrées à
  5.265,60 MDH1, soit un taux d’émission de 50,37%, dont 2.334,70 MDH au titre des
  dépenses d’exploitation avec un taux d’émission de 59,30% et de 317,61 MDH au titre
  des dépenses d’investissement avec un taux d’émission de 23,91%.
► Les SEGMA opérant dans le domaine de la santé, dans le domaine des activités
  récréatives et dans le domaine des autres actions sociales ont réalisé les taux
  d’émissions les plus élevés, soient respectivement 67,27%, 59,87% et 56,39%.
► Le taux global de couverture des dépenses par les recettes propres s’élève à 91,39%
  en 2023 contre 65,64% en 2022, soit une augmentation de 25,75 points qui peut être
  expliquée par la reprise de l’économie nationale et la récupération des marges
  perdues durant la crise sanitaire. Ainsi, certains services ont réalisé des taux de
  couverture relativement élevés en 2023. Il s’agit, à titre d’illustration, des services
  intervenant dans le domaine de l’équipement, du transport et autres infrastructures
  économiques, et ceux relevant du domaine des pouvoirs publics et services
  généraux, ayant réalisé des taux de couverture atteignant respectivement 158,10% et
  128,85%.

Le présent rapport comporte trois parties principales :
► Une première partie porte sur l’évolution du nombre de SEGMA et leur répartition
  par domaine d’intervention au titre de l’année budgétaire 2024 ;
► Une deuxième partie portant sur le bilan des réalisations financières des SEGMA au
  titre de l’année 2023, en comparaison avec celui de 2022, et ce, par le biais d’une
  analyse des encaissements des recettes et des émissions des dépenses, ainsi que la
  contribution des SEGMA selon leur domaine d’intervention ;
► Une troisième partie présente les réalisations physiques des SEGMA durant l’année
  2023 et l’état d’avancement de leurs plans d’action en 2024, ainsi que leurs
  programmes d’action prévus dans le cadre du Projet de Loi de Finances de l’année
  budgétaire 2025.
L’accent est mis également sur les objectifs et les indicateurs permettant d’apprécier
l’effort consenti par ces services en termes d’amélioration de la qualité des prestations
rendues aux citoyens.



1 Compte tenu des excédents reportés de l’exercice précèdent.
                                    RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


        EVOLUTION DU                      NOMBRE            DE     SEGMA          PAR       DOMAINE
        D’INTERVENTION
1.1. Stock des SEGMA sur la période 2018-2024

Au titre de l’année 2024, et pour la deuxième année consécutive, le nombre de SEGMA
s’est établi à 171 services. Cette année a été donc marquée par l’absence de création
de nouveaux SEGMA ou de suppression de SEGMA existants.




                     Graphe 1 : Évolution du nombre de SEGMA pendant la période 2018-2024

1.2. Répartition des SEGMA par domaine d’intervention en 2024

►     Les SEGMA opérant dans le domaine de la santé sont au nombre de 91
      SEGMA. Ils représentent 53,2% des 171 SEGMA inscrits au titre de la Loi de Finances
      2024 et sont composés de :
                                            Domaine de la santé
 77 Centres Hospitaliers ;
 7 Hôpitaux Militaires et 2 Centres Médico-Chirurgicaux ;
 Centre National de Transfusion Sanguine et d’hématologie ;
 Centre Régional de Transfusion Sanguine - Casablanca ;
    Institut National d’Hygiène (INH) ;
 Centre National de Radio-Protection (CNRP) ;
 Direction du Médicament et de la Pharmacie (DMP).

►     Les SEGMA opérant dans le domaine de l’enseignement, de la formation
      professionnelle et de la formation des cadres sont au nombre de 44, soit 25,7% de
      l’ensemble des SEGMA existants. Ils se présentent comme suit :
     PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



Domaine de l’enseignement, de la formation professionnelle et de la formation des cadres
 4 Services œuvrant dans le domaine Touristique ;
 8 Ecoles et Instituts Agricoles ;
 2 Instituts de Formation sur les métiers des Mines ;
 6 Services œuvrant dans le domaine de l’Artisanat ;
 6 Services œuvrant dans le domaine de la Pêche Maritime ;
 5 Ecoles de formation dans le domaine de l’Urbanisme et de l’Aménagement du Territoire ;
 13 Services et Instituts chargés de la formation dans divers domaines (information, infrastructures, ...).

Pour le reste des SEGMA qui représentent 21,1% des services existants, ils sont répartis
par domaine d’intervention comme suit :

      Domaine de l’équipement, du transport et autres infrastructures économiques
      avec 16 SEGMA, soit 9,4% des SEGMA inscrits au titre de la Loi de Finances 2024:
            Domaine de l’équipement, du transport et autres infrastructures économiques
      Centre National d’Études et de Recherches Routières (CNERR) ;
 •    10 Services de Logistique et de Matériel (SLM)
 •    Service du Réseau des SLM ;
 •    Direction Générale de l’Aviation Civile (DGAC)
 •    Direction de la Marine Marchande (DMM) ;
 •    Service de Gestion des Chantiers (SGC) ;
 •    Direction Générale de la Météorologie (DGM).

      Domaine des pouvoirs publics et des services généraux avec 9 SEGMA, soit 5,3%
      des 171 SEGMA inscrits au titre de la Loi de Finances 2024 :
                            Domaine des pouvoirs publics et services généraux
     Trésorerie Générale du Royaume (TGR) ;
     Administration des Douanes et Impôts Indirects (ADII) ;
     Unité de Fabrication de Masques de la Gendarmerie Royale (UFM)
     Direction de l’imprimerie Officielle (DIO)
     Imprimerie Dar AL Manahil ;
     Centre Royal de Télédétection Spatiale (CRTS) ;
     Centre National de Documentation (CND) ;
     Centre de Publication et de Documentation Judiciaire de la Cour de Cassation (CPDJ)
     Etablissement Central de Gestion et de Stockage des Matériels (ECGSM).

►     Domaine des activités récréatives avec 5 SEGMA, soit 2,9% des 171 SEGMA inscrits
      au titre de la Loi de Finances 2024 :
                                      Domaine des activités récréatives
     Complexe Sportif Mohammed V de Casablanca et base nautique de Mohammedia ;
     Service du Contrôle des Établissements et des Salles Sportives ;
     Complexe Moulay Rachid de la Jeunesse et de l’Enfance de Bouznika ;
     Royal Golf Dar Es-Salam ;
     Musée Mohammed VI pour la Civilisation de l’Eau au Maroc.
                                    RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


     Domaine de l’agriculture et de la pêche maritime avec 2 SEGMA, soit 1,2% des 171
     SEGMA inscrits au titre de la Loi de Finances 2024 :
                          Domaine de l’agriculture et de la pêche maritime
    Division de la Durabilité et d’Aménagement des Ressources Maritimes (DDARM) ;
    Laboratoire National des Etudes et de Surveillance de la Pollution (LNESP).

     Domaine des autres actions sociales avec 3 SEGMA, soit 1,7% des 171 SEGMA inscrits
     dans la Loi de Finances 2024 ;
                                    Domaine des autres actions sociales
    Division du Pèlerinage (DP) ;
    Service des Unités de Formation Artistique et Artisanale (SUFAA) ;
    Direction des Affaires Consulaires et Sociales (DACS).

►     Domaine des autres actions économiques avec 1 SEGMA, soit 0,6% des 171 SEGMA
      inscrits au titre de la Loi de Finances 2024 :
                               Domaine des autres actions économiques
    SEGMA chargé de la Privatisation.

La répartition des SEGMA par domaine d’activité, illustrée dans le graphique ci-après,
indique la prédominance des SEGMA à caractère social avec 81% du nombre total des
SEGMA (soit 138 SEGMA sur un total de 171), notamment, le domaine de la santé (avec
91 SEGMA) et le domaine de l’enseignement, de la formation professionnelle et de la
formation des cadres (avec 44 SEGMA).




                 Graphe 2 : Répartition des SEGMA par domaine d’activité au titre de l’année 2024
   PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



II. BILAN D’EXECUTION DES BUDGETS DES SEGMA AU TITRE DES
   ANNEES 2022 - 2023
L’exécution des budgets des SEGMA, au titre de l’année 2023, présente un solde
positif de l’ordre de 3.812,20 MDH en fin d’année. Cet excédent est enregistré
principalement par les SEGMA oeuvrant dans le domaine de la santé à concurrence de
42,87%, et dans une moindre mesure par les SEGMA couvrant le domaine des pouvoirs
publics et des services généraux et celui de l’équipement, du transport et des autres
infrastructures économiques à hauteur de 21,57% et 21,22% respectivement.

11.1 . Evolution de la structure globale des recettes des SEGMA en termes de
      recettes propres et de dotations d’équilibre du budget général
Au titre de l’année 2023, le montant global des recettes2 a atteint 6.464,50 MDH. Ce
niveau a dépassé le montant des prévisions actualisées situé aux alentours de 5.055,91
MDH, soit un taux de réalisation de 127,86%. En effet :

     Les recettes propres ont enregistré un montant de 2.423,99 MDH contre des
     prévisions actualisées de l’ordre de 1.374,09 MDH, soit un taux global de
     recouvrement de 176,41%. Elles sont principalement réalisées par les SEGMA œuvrant
     dans le secteur de la santé avec un taux de 64,91%, ainsi que par les SEGMA opérant
     dans le domaine de l’équipement, du transport et des autres infrastructures
     économiques et dans celui des pouvoirs publics et des services généraux à hauteur
     de 15,13% et 12,90% respectivement.

                                                                      Pouvoirs publics et services
   Santé                                                                       généraux
    65% _                                                                        13%

                                                                                       Enseignement, formation
                                                                                      professionnelle et formation
                                                                                               des cadres
                                                                                                   3%



                                                                                      Equipement, Transport et
                                                                                        autres infrastructures
                                                                                            économiques
                                                                                                 15%

                               Autres actions social          Activités récreatives
                                         1%                            3%


                  Graphe 3 : Répartition des recettes propres des SEGMA par domaine d’activité en 2023

► Le taux de recouvrement des recettes propres, ainsi que leur répartition par domaine
  d’activité au titre de l’année 2023, sont illustrés dans le graphique ci-après :


2 Intégrant les excédents reportés de l’exercice précédent.
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME




      Graphe 4 : Taux de recouvrement des recettes propres des SEGMA par domaine d’activité en 2023

   Les dotations d’équilibre, versées par le budget général à certains SEGMA, s’élèvent
   à 918,93 MDH en 2023 contre 884,64 MDH en 2022, soit une augmentation de l’ordre
   de 3,88% ;
► Le total des excédents d’exploitation et d’investissement à fin 2022 reporté en
  additionnel aux crédits de l’année 2023 se chiffre à 3.121,59 MDH, contre 3.190,53
  MDH enregistré à fin 2021, soit une diminution de l’ordre de 2,16%. Ainsi, il y a lieu de
  constater que les excédents représentent 48,29% des recettes des SEGMA en 2023,
  contre 37,50% pour les recettes propres et 14,21% pour les dotations d’équilibre du
  budget général.
Le graphe ci-après illustre la structure globale des recettes des SEGMA en 2022 et
2023 :
                   2022                                          2023




                       Graphe 5 : Structure des recettes des SEGMA en 2022 et 2023

Par conséquent, le taux de couverture des dépenses par les recettes propres s’élève à
91,39% en 2023, contre 65,64% en 2022, soit une augmentation de 25,75 points qui
peut être expliquée par la reprise de l’économie nationale et la récupération des
marges perdues durant la crise du Covid-19.
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


11.2 . Ventilation des dépenses des SEGMA par nature et par domaine d’activité
Les émissions des dépenses de l’ensemble des SEGMA s’élèvent à 2.652,31 MDH en
2023, par rapport à des crédits ouverts de l’ordre de 5.265,60 MDH, soit un taux
d’émission global de 50,37%. Ces dépenses se répartissent, par nature, comme suit :
    Des dépenses d’exploitation émises de l’ordre de 2.334,70 MDH par rapport à des
    crédits ouverts de 3.937,42 MDH, soit un taux d’exécution de 59,30% ;
► Des dépenses d’investissement émises d’environ 317,61 MDH par rapport à des
  prévisions de l’ordre de 1.328,18 MDH, soit un taux d’exécution de 23,91%.
Le graphique ci-dessous montre la structure des dépenses des SEGMA émises en
2023 :




                     Graphe 6 : Structure des dépenses des SEGMA au titre de l’année 2023

Il est à signaler que ces dépenses ont été exécutées à concurrence de 67,27% par les
services opérant dans le domaine de la santé, et à hauteur de 59,87% et de 56,39%
respectivement par ceux oeuvrant dans le domaine des activités récréatives et le
domaine des autres actions sociales.
Le graphique ci-après présente la ventilation, par domaine d’activité, des dépenses
réalisées par les SEGMA en 2023 :

                        Pouvoirs publics et        Equipement, Transport et autres
      Agriculture et                                 infrastructures économiques
                        services généraux
          pêche                                   9               9%
                                9%,
        maritime
           1%

        Activités^
       récréatives
           3%


      Enseignement,
        formation
      professionnel
      e et formation
        des cadres          Autres actions                                                  _Santé
             9%                sociales                                                       66%
                                 3%


 Graphe 7 : Répartition par domaine d’intervention des dépenses des SEGMA exécutées au titre de l’année 2023
                                       RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


III. BILAN D’ACTIVITE 2023-2024 ET PLAN D’ACTION 2025
111. 1. Domaine de la santé


Les principales actions réalisées par les hôpitaux publics au titre de l’année 2023 sont
présentées dans le tableau ci-dessous :
                                                                      Indicateur                                    Taux de
         Objectif                Mesures prises                                                   Réalisations
                                                                       de suivi                                    réalisation
                         Amélioration       des             - Taux d’hospitalisation ;               3,37%3
    Améliorer l’accès
                         conditions d’accueil, et
     aux soins et la
                         développement      des
     prise en charge                                        - Taux de césarienne.                    15,21%4
                         fonctions   support à
       hospitalière
                         l’hôpital.
                         Préparation des CHR au             - Nombre       de     centres
                         processus                            hospitaliers    régionaux
                                                                                                        6              100%
                         d’accréditation                      engagés dans le processus
                         hospitalière.                        d’accréditation.
      Améliorer la
      gestion de la
                                                            - Nombre d’hôpitaux ayant
    qualité au niveau    Formation des équipes                déployés le système de                   130             100%
           des           hospitalières sur    la
     établissements                                           notification           des
                         procédure         de
        de soins                                              événements indésirables ;
                         déclaration       des
                         événements                         - Nombre d’établissements
                         indésirables.                        hospitaliers formés en
                                                              sécurité des patients.                   130             100%


                         Etude et conclusion des
                         conventions          de            - Nombre      de   centres
                         construction         et              d’Hémodialyse créés dans
                                                                                                   5 centres           50%
      Développer         d’équipement et appui                le cadre des conventions
       l’offre en        aux             centres              de partenariat.
    Hémodialyse et       d’Hémodialyse.
     améliorer ses       Renforcement       du
     performances        partenariat  avec   le
                                                            - Nombre de patients pris
                         secteur privé pour la                                        6031 patients                    80%
                                                              en charge.
                         résorption des listes
                         d’attentes.

Au cours du premier semestre de l'année 2024, les hôpitaux publics ont poursuivi leurs
efforts en matière de réalisation de missions de supervision, de l’aménagement et du
renforcement des équipements médicotechniques des services d'accueil des
urgences,    ainsi  que    l’accompagnement      des équipes       hospitalières pour
l’implémentation des nouvelles procédures de facturation et remboursement
spécifiques à l’« AMO TADAMONE ». De plus, l’année 2024 a connu le démarrage des

3
  Cet indicateur tient compte de plusieurs variables dépendantes du développement de l’offre hospitalière et des programmes
hospitaliers ainsi que du développement de l’offre hospitalière privée. L’interprétation de cet indicateur devra tenir également
compte du développement rapide de la population des bassins de desserte (communes et arrondissements) qui constitue le
dénominateur de cet indicateur.
4 Cet indicateur est calculé sur la base du dénominateur accouchements en milieu hospitalier. L’objectif recommandé par
l’OMS de 10% est, quant à lui, calculé sur la base d’un dénominateur incluant l’ensemble des accouchements attendus.
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


activités du Programme d’Appui à la Réforme du Secteur de la Santé « PASSIII » dans
le cadre de l’assistance technique « préparation et riposte aux crises » pour le pôle des
établissements de soins hospitaliers.
Le plan d’action de ces SEGMA au titre de l’année 2025 vise à rendre l’offre
hospitalière accessible, disponible, globale, prodiguant des soins sûrs et de qualité, et
à remédier ainsi aux différents dysfonctionnements de l’hôpital public, à travers la
réalisation des actions suivantes :
► Accompagnement des établissements hospitaliers dans l'élaboration des plans
  d'urgence hospitalières, ainsi que la mise en place des filières des urgences
  spécialisées ;
► Renforcement des ressources humaines des urgences ;
► Amélioration de la facturation hospitalière à travers la réalisation du guide de
  facturation et l’accompagnement des hôpitaux pour pallier les dysfonctionnements
  liés à la facturation ;
► Développement de l’attractivité territoriale des hôpitaux publics et amélioration de
  la qualité du séjour des patients, en révisant les termes de référence des prestations
  sous-traitées ayant un impact direct sur la qualité du séjour et les prestations
  hospitalières ;
► Renforcement des capacités nationales, régionales et locales en matière de gestion
  des risques sanitaires et des catastrophes.
III.1.2. Centres de Transfusion Sanguine et d’Hématologie

Au titre de l’année 2023, le nombre des donneurs de sang recensés au niveau des
Centres de Transfusion Sanguine (CTS) et dans les différents établissements a atteint
382.234 donneurs, soit une augmentation de 10,4% par rapport au chiffre réalisé en
2022 qui était de 346.212 donneurs. Cette augmentation s’explique notamment par la
sensibilisation à travers les réseaux sociaux, le recours à des spots radio sur la
promotion au don de sang et l’organisation de journées portes ouvertes au niveau des
sites fixes des Centres Régionaux de Transfusion Sanguine (CRTS).
Les principales actions réalisées lors du premier semestre de l’année 2024 par les
CTS, se présentent comme suit :

   L’organisation de journées portes ouvertes au niveau des sites fixes des CRTS ;
   La célébration au sein des CRTS de la journée mondiale de la femme au 8 mars, la
   journée mondiale du don de sang au 14 juin et la journée Maghrébine au 31 mars ;
   Le renforcement des partenariats avec les anciens partenaires du centre de
   transfusion sanguine et d’hématologie (CNTSH) et l’organisation des collectes du
   sang en collaboration avec le Ministère de l’intérieur, le Ministère des Habous et des
   Affaires Islamiques, la Direction Générale de Sûreté Nationale (DGSN), les Forces
   Auxiliaires et la Gendarmerie Royale.
                                     RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


Au titre de l’année 2025, les CTS envisagent la poursuite des actions entamées durant
les exercices précédents, qui s’articulent autour des axes suivants :
► L’instauration d’un nouveau cadre du système national de transfusion sanguine ;
► L’amélioration des équipements et logistiques pour les équipes fixes et mobiles ;
► L’amélioration de l'autosuffisance en médicaments dérivés de sang ;
► Le renforcement des capacités techniques du CNTSH et des CRTS.

Il1.1.3. Centre National de Radioprotection

Le bilan d’activité du Centre National de Radioprotection (CNRP) au titre de l’année
2023, et du premier semestre de l’année 2024 et les prévisions pour l’exercice 2025
se présentent dans le tableau ci-après :
                       Actions                           Réalisations 2023        Réalisations 2024       Prévisions 2025
    Contrôle de conformité aux normes de                                                  32                     220
 radioprotection des installations médicales, 76 établissements                    Etablissements          Etablissements
       industrielles et des laboratoires          contrôlés
                                                                                      contrôlés               contrôlés
       d’enseignement et de recherche
  Surveillance dosimétrique des travailleurs
                                                    41.500                                                     80.000
  affectés aux travaux sous rayonnements                                           41.035 analyses
                                                   analyses                                                    analyses
                   ionisants
     Contrôle radiologique aux frontières        21 contrôles                       25 contrôles       50 contrôles
   Surveillance de l’environnement et des             751                               459
                                                                                                      1.100 analyses
            denrées alimentaires                   analyses                           analyses
       Etalonnage et métrologie des                   731                               105
                                                                                                     300 opérations
           rayonnements ionisants                 opérations                         opérations
                                                                                     En cas de
       Interventions en cas d’urgence                            02                                         10
                                                                                      nécessité
                                                                                Participation de 44
                                                         Participation de        cadres du CNRP à     Participation
                                                          35 cadres du                               de 100 cadres
                                                                                 des ateliers et des
                                                           CNRP à des           stages de formation     du CNRPà
                     Formation
                                                          ateliers et des                            des ateliers et
                                                                                  organisés par le
                                                            stages de             CNRP, l'AlEA et    des stages de
                                                            formation                l’AASN             formation
(*) AIEA : Agence Internationale de l’Energie Atomique / AASN : Administration Américaine de Sécurité Nucléaire.


ill.1.4. Institut National d’Hygiène

Au titre de l’année 2023 et du premier semestre de 2024, l’institut National
d’Hygiène (INH) a centré ses travaux autour de la réalisation de plusieurs types
d’analyses et de tests dans différents domaines. Ainsi, les actions suivantes ont été
réalisées :
 ► Assurer les prestations de services et d’expertises dans le domaine de la Biologie
    médicale et santé environnementale ;
     Assurer l’appui technique et scientifique aux programmes de santé publique ;
     Encourager la recherche et le développement dans le domaine de la santé ;
► Réaliser des missions de supervision des laboratoires ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


► Contribuer à la formation dans les domaines relevant de ses compétences.
En plus du développement et de l’amélioration de l’ensemble des activités présentées
plus-haut, l’INH envisage d’assurer au titre de l’année 2025 l’appui technique et
scientifique aux programmes de santé publique, la veille et la surveillance
épidémiologique, ainsi que l’amélioration continue du système de management de
qualité (SMQ).

111.1.5. Direction du Médicament et de la Pharmacie

Les réalisations de la Direction du Médicament et de la Pharmacie (DMP) au titre de
l’année 2023 et du premier semestre de l’année 2024 se résument comme suit :

                                                                                                     Taux de
        Objectifs                                 Principales actions réalisées
                                                                                                   réalisation
 Création de l’Agence
                             Adoption du projet de la loi n° 10.22 portant création de
    Marocaine des
                             l'Agence Marocaine des Médicaments et des Produits de                    90%
 Médicaments et des
                             Santé, et préparation de ses textes d’application.
  Produits de Santé
                             Organisation d’ateliers avec les partenaires nationaux en vue
   Elaboration de la         de :
 nouvelle édition de la      -L’évaluation de la PPN 2015-2020 et la formulation des
       Politique             recommandations et des propositions pour la PPN 2021­                    100%
   Pharmaceutique            2025 ;
   Nationale (PPN)           -La discussion des indicateurs de suivi, la validation et
                             l’adoption finale de la nouvelle édition de la PPN 2021-2025.
Formation du personnel
       sur toutes les
techniques de transfert       Participation aux formations assurées par Walvax ;
    technologique du                                                                                  60%
 procédé de fabrication      Contrôle qualité du 1er vaccin fabriqué par une industrie
   et des méthodes de        pharmaceutique marocaine.
contrôle de vaccins par
les laboratoires chinois
          Walvax
    Renforcement du
                             - Achat du matériel, réactifs et fongibles nécessaires ;
   contrôle qualité des
                             - Achat d’un appareil de contrôle qualité des médicaments et            100%
 vaccins et des dérivés
                             des dérivés.
          de sang
  Information du public      Publication et mise à jour de la liste des médicaments
   sur les médicaments       enregistrés au Maroc sur le site web de la direction.                    100%
  enregistrés au Maroc
   Fixation du prix des      - Evaluation de tous les dossiers conformes ;                             89%
     médicaments et          - Accélération de la publication au BO des prix des nouveaux
    publication au BO        médicaments.                                                              74%
                             Inspection des :
                             - Etablissements pharmaceutiques industriels ;                            15 %
                             - Etablissements Pharmaceutiques Grossistes (EPGR) ;                     100 %
   Renforcement du           - Etablissements pharmaceutiques vétérinaires ;                          60%
  contrôle du secteur
   pharmaceutique            - Office national de sécurité         sanitaire      des   produits      14 %
                               alimentaires (ONSSA) ;
                             - Etablissements des dispositifs médicaux ;                              48 %
                             - Réserves des médicaments dans les cliniques.                           67 %
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


                                                                                                Taux de
        Objectifs                              Principales actions réalisées
                                                                                              réalisation
                            - Collaboration avec le Parquet dans le cadre de la lutte
                              contre le circuit illicite des médicaments et des produits de
  Lutte contre le circuit     santé ;
illicite des médicaments    - Désignation d'un expert du Département de l'inspection et          100%
et des produits de santé      de suivi du secteur auprès du Parquet Général ;
                            - Réalisation d’une série d’enquêtes.

Au titre de l’année 2025, la DMP envisage la poursuite des actions entamées durant
les exercices précédents, qui s’articulent autour des axes suivants :

► La poursuite de la mise en place de l’Agence Marocaine des Médicaments et des
  Produits de la Santé, à travers la préparation et l’approbation de l’organigramme et
  des statuts de l’agence ;
► L’accélération du processus de dématérialisation des procédures, à travers la
  dématérialisation des procédures de réception et de délivrance des autorisations et
  des certificats, et l’instauration d’un système de gestion de l’information du
  laboratoire (LIMS) ;
► Le renforcement du cadre légal et législatif du secteur pharmaceutique ;
► L’élaboration d’un plan national de lutte contre les ruptures d’approvisionnement de
  médicaments en concertation avec les parties prenantes ;
► La mise en oeuvre d’un programme annuel de surveillance post-commercialisation
  des produits médicaux.

Il1.1.6. Hôpitaux et Centres Médico-Chirurgicaux Militaires

Au titre de l’exercice 2023, les principales actions réalisées par les sept hôpitaux
militaires et les deux centres médico-chirurgicaux militaires se présentent comme
suit :
► L’approvisionnement permanent des hôpitaux en produits pharmaceutiques
  consommables, fongibles et réactifs et en produits biologiques et chimiques,
  conformément aux besoins identifiés par les services médico-hospitaliers et
  médicotechniques ;
► La réalisation des opérations d’entretien, de réparation du matériel et de
  maintenance des installations techniques ;
► La modernisation et la rénovation des plateaux médicotechniques et des blocs
  opératoires pour l’amélioration de la prise en charge des patients, à travers
  l’acquisition de matériaux pour les spécialités nouvellement mises en place, et le
  remplacement du matériel présentant des performances limitées ;
   L’amélioration des conditions d’accueil et de bien-être des malades et du personnel à
   travers l’acquisition de moyens de transport, l’aménagement des salles de
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


   consultation, des aires d’attente et des espaces verts ainsi que l’entretien des locaux
   et des chambres ;
► Le raffermissement des plateaux informatiques et techniques en les dotant
  d’équipements et des logiciels nécessaires.

Par ailleurs, l’élaboration du plan d’action au titre de l’année 2024 a été effectuée dans
un souci d’une large efficacité en prenant en considération les orientations
stratégiques des hôpitaux et centres médico-chirurgicaux à travers l’adoption d’une
approche participative et d’un esprit d’initiative dans le but de préserver les acquis
encaissés. A ce titre, ces centres et hôpitaux visent à mettre en concordance
l’avancement des principaux projets inscrits dans le programme 2024 avec les
échéances exigées et préétablies , notamment en ce qui concerne l’approvisionnement
suffisant en médicaments, consommables, fluides médicaux et produits biologiques et
chimiques, l’élargissement de la population des bénéficiaires des services des hôpitaux
militaires, l’amélioration du cadre de travail du personnel et de prise en charge des
malades et la modernisation et l’équipement des hôpitaux par l’acquisition du matériel
médicotechnique et médico-hospitalier, et ce, tout en veillant à l’amélioration de la
qualité des prestations, de la performance d’accueil et d’hébergement, de la sécurité
et de l’activité hospitalière, ainsi qu’à la digitalisation des services et l’entretien des
locaux.

Quant au plan d’action 2025, les hôpitaux et centres médico-chirurgicaux visent à
maîtriser et rationaliser les dépenses de fonctionnement, tout en maintenant le niveau
et la qualité des services et des prestations rendus aux patients. Cette approche, à la
fois concrète et méthodique, vise à encourager l’esprit d’efficacité et de rendement, et
à initier le passage vers une logique de résultats axée sur la performance. Cette vision
stratégique sera traduite en différents projets, déclinés en actions réalisables
permettant d’assurer la continuité dans la modernisation et la rénovation des
infrastructures et matériaux, de garantir le bon fonctionnement des équipements
médicotechniques et techniques existants, et de renforcer le soutien administratif et
logistique devant accompagner la production d’une prestation médicale de qualité.

III.2. Domaine de l’enseignement, de la formation professionnelle et de la
       formation des cadres

Il1.2.1. SEGMA relevant du département du Tourisme

Les SEGMA relevant du département du Tourisme sont au nombre de deux Instituts
Spécialisés de Technologie Appliquée Hôtelière et Touristique (ISTAHT), l’institut
Supérieur International du Tourisme (ISIT), et le Centre de Qualification
Professionnelle Hôtelière et Touristique (CQPHT) de Touarga-Rabat. Au titre de
l’année 2023 et du premier semestre de 2024, les principales actions réalisées par ces
services sont les suivantes :
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► Le suivi du projet de repositionnement de l’institut Supérieur International de
  Tourisme de Tanger en tant que business school d’excellence à vocation africaine, à
  travers l’adaptation de l’arsenal juridique avec la nouvelle vision de l’institut, la mise
  à niveau de ses infrastructures et des équipements et le renforcement de l'équipe
  pédagogique ;
► Le suivi des travaux d’extension et de réhabilitation, dans le cadre du fonds "Sharaka''
  de l’ISTAHT de Tanger et de Ouarzazate, ainsi que les travaux de réaménagement du
  CQPHT de Touarga-Rabat ;
► L’amélioration de l’attractivité des instituts par le biais de l’organisation des
  caravanes de communication dans les lycées et les collèges des régions ;
► La coopération dans le domaine du transport maritime des passagers, avec l'agence
  de coopération internationale espagnole pour le développement, afin de faciliter
  l’insertion professionnelle des stagiaires ;
► Le renforcement des ressources humaines à travers le recrutement de formateurs et
  d’enseignants ;
► Sensibilisation du personnel et des stagiaires sur la préservation des ressources et de
  l’environnement ;
►   L’implication de l’établissement et des stagiaires dans des activités communautaires ;
► La mise en oeuvre de la langue amazighe au sein des instituts de formation hôtelière
  et touristique ;
► L’élaboration de l’offre de formation 2024/2025 à travers la planification stratégique
  et la détermination des prérequis pour l’accès à la formation au sein des instituts du
  tourisme ;
► Le renforcement des partenariats internationaux dans le domaine de la formation
  hôtelière et touristique.
Le plan d’action de ces SEGMA au titre de l’année 2025 prévoit la réalisation des
actions suivantes :
► L’organisation des formations continues au profit des professionnels du secteur en
  vue de la mise en oeuvre du catalogue de formation continue développé dans le
  cadre du « Fonds Sharaka » ;
► Le suivi du projet de repositionnement de l’institut Supérieur International de
  Tourisme de Tanger ;
►   L’élaboration de l’offre de formation de l’année 2025/2026 ;
► La veille sur les activités pédagogiques des établissements de formation hôtelière et
  touristique ;
► La création des Instances de Gouvernance : le conseil de l’Etablissement et le conseil
  de gouvernance et de coordination pédagogique.
    PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


 III.2.2. SEGMA rattachés au département de I3Artisanat

 Le bilan des réalisations des six Instituts Spécialisés des Arts Traditionnels (ISAT) au titre de
 l’année 2023 se présente comme suit :
Etablissement de           Actions réalisées        Indicateurs de suivi          Réalisations          Taux de
   formation                                                                                           réalisation
                                                       Effectif des
                   Formation initiale des jeunes                                      72                 60%
                                                         inscrits
    Institut       Organisation des sessions de
                                                       Nombre de
 Spécialisé des    formation    continue    des                                      300                100%
                                                      bénéficiaires
      Arts         artisans
Traditionnels de                                                           50% de modules pour les
                   Formation des stagiaires
   Marrakech                                    Modules de                   stagiaires en 1ère A et
                   dans     le    domaine de                                                            100%
                                             formation réalisés             100% pour ceux en 2ème
                   l’éducation financière
                                                                                       A
                                                       Effectif des
                   Formation initiale des jeunes                                      212                73%
                                                         inscrits
    Institut       Élaboration des plans de                                Élaboration de 100% des
                                              Plans de formation
 Spécialisé des    formation selon l’approche                                plans des modules de       100%
                                                   élaborés
      Arts         compétence                                                      formation
Traditionnels de                                                           50% de modules pour les
                   Formation des stagiaires
       Fès                                      Modules de                   stagiaires en 1ère A et
                   dans     le    domaine de                                                            100%
                                             formation réalisés             100% pour ceux en 2ème
                   l’éducation financière
                                                                                       A
                                                       Effectif des
                   Formation initiale des jeunes                                      197                90%
                                                         inscrits
                   Implantation du programme
                                                                            Implantation de 100%
                   de gestionnaire d’unité de Plans de formation
                                                                           des plans de modules de      100%
    Institut       production    en   ferronnerie   élaborés
                   d’art
                                                                                  formation
 Spécialisé des
      Arts         Validation   des   acquis de
                                                   Nombre de
 Traditionnels     l’expérience   professionnelle                                     151               100%
                                                  bénéficiaires
 d’Ouarzazate      des artisans
                                                                           50% de modules pour les
                   Formation des stagiaires
                                                Modules de                   stagiaires en 1ère A et
                   dans     le    domaine de                                                            100%
                                             formation réalisés             100% pour ceux en 2ème
                   l’éducation financière
                                                                                       A
                                                       Effectif des
                   Formation initiale des jeunes                                     265                 90%
                                                         inscrits
    Institut       Organisation des sessions de
                                                       Nombre de
 Spécialisé des    formation    continue    des                                      100                100%
                                                      bénéficiaires
      Arts         artisans
 Traditionnels                                                             50% de modules pour les
                   Formation des stagiaires
  d’Inezgane                                    Modules de                   stagiaires en 1ère A et
                   dans     le    domaine de                                                            100%
                                             formation réalisés             100% pour ceux en 2ème
                   l’éducation financière
                                                                                       A
                                                       Effectif des
                   Formation initiale des jeunes                                      87                 67%
                                                         inscrits
                 Élaboration des plans de                        Élaboration de 100% des
                                              Plans de formation
                 formation selon l’approche                        plans des modules de                 100%
    Institut                                       élaborés
                 compétence                                              formation
 Spécialisé des
                 Organisation des sessions de
      Arts                                        Nombre de
                 formation     continue   des                               120                         100%
Traditionnels de                                 bénéficiaires
                 artisans
    Meknès
                                                                 50% de modules pour les
                 Formation des stagiaires
                                                  Modules de       stagiaires en 1ère A et
                 dans     le    domaine    de                                                           100%
                                              formation réalisés  100% pour ceux en 2ème
                 l’éducation financière
                                                                             A
                                   RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME

 Etablissement de                                                                                       Taux de
    formation              Actions réalisées        Indicateurs de suivi          Réalisations         réalisation
                                                       Effectif des
                    Formation initiale des jeunes                                     74                   52%
                                                         inscrits
                 Organisation des sessions de
                                                  Nombre de
                 formation     continue   des                                        410                   100%
    Institut                                     bénéficiaires
                 artisans
 Spécialisé des
                 Validation des acquis de
      Arts                                        Nombre de
                 l’expérience professionnelle                                        328                   100%
Traditionnels de                                 bénéficiaires
                 des artisans
     Rabat
                                                                           50% de modules pour les
                 Formation des stagiaires
                                                  Modules de                 stagiaires en 1ère A et
                 dans     le    domaine    de                                                              100%
                                              formation réalisés            100% pour ceux en 2ème
                 l’éducation financière
                                                                                       A

 Au cours du premier semestre de l’année 2024, le plan d’action des ISAT est présenté dans le
 tableau ci-dessous :
 Etablissement        Plan d’action au titre de
                                                            Actions réalisées ou en cours de réalisation
 de formation               l’année 2024
                                               Inscription de 83 jeunes en mode résidentiel sur une
                    Formation initiale des jeunes
                                               prévision de 120 inscrits
    Institut     Organisation de sessions de Formation de 96 artisans et artisanes en partenariat
 Spécialisé des     formation continue des     avec l’UNESCO et la Fondation Mohamed V pour la
      Arts                   artisans          Solidarité
Traditionnels de     Validation des acquis
                                               Certification de 100 artisans et artisanes
   Marrakech      professionnels des artisans
                  Programme de l’éducation Réalisation de 50% des modules pour les stagiaires
                           financière          dans le domaine de l’éducation financière
                                               Inscription effective de 393 jeunes, dont 149 en mode
    Institut     Formation initiale des jeunes résidentiel et 244 en mode apprentissage, sur une
 Spécialisé des                                prévision de 410 inscrits
      Arts           Validation des acquis     Certification de 380 artisans et artisanes en partenariat
Traditionnels de professionnels des artisans avec la Chambre d’Artisanat
       Fès        Programme de l’éducation Réalisation de 50% de modules pour les stagiaires dans
                           financière          le domaine de l’éducation financière
                                               Inscription de 208 jeunes dont 95 en mode résidentiel
                 Formation initiale des jeunes
    Institut                                   et 113 en mode apprentissage sur 263 inscrits prévus
 Spécialisé des  Organisation de sessions de
                                               Formation de 270 artisans et artisanes en partenariat
      Arts          formation continue des
                                               avec la Chambre d’Artisanat
 Traditionnels               artisans
 d’Ouarzazate     Programme de l’éducation Réalisation de 50% de modules pour les stagiaires dans
                           financière          le domaine de l’éducation financière
                                               Inscription de 309 jeunes dont 259 en mode résidentiel
                 Formation initiale des jeunes
                                               et 50 en mode apprentissage sur 310 inscrits prévus
    Institut     Organisation de sessions de
                                               Formation de 100 artisans dans les métiers d’artisanat
 Spécialisé des     formation continue des
                                               en partenariat avec la Chambre d’Artisanat.
      Arts                   artisans
 Traditionnels       Validation des acquis     Certification de 100 artisans et artisanes dans les
  d’Inezgane      professionnels des artisans métiers d’artisanat
                  Programme de l’éducation Réalisation de 50% de modules pour les stagiaires dans
                           financière          le domaine de l’éducation financière
                                               Inscription de 87 jeunes dont 42 en mode résidentiel et
    Institut     Formation initiale des jeunes
                                               45 en mode apprentissage sur 135 inscrits prévus
 Spécialisé des
                  Amélioration de la qualité   Implantation de 100% des plans de modules du
      Arts
                         de formation          programme Damasquinerie.
    PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


 Etablissement       Plan d’action au titre de
                                                                Actions réalisées ou en cours de réalisation
 de formation              l’année 2024
Traditionnels de      Validation des acquis    Certification de 200 artisans et artisanes dans les
    Meknès         professionnels des artisans métiers d’artisanat
                   Programme de l’éducation    Réalisation de 50% de modules pour les stagiaires dans
                             financière        le domaine de l’éducation financière
                                               Inscription de 73 jeunes dont 13 stagiaires en mode
                 Formation initiale des jeunes
                                               résidentiel et 60 apprentis sur 150 inscrits prévus
                 Organisation de sessions de
    Institut                                   Formation de 500 artisans et artisanes en partenariat
                 formation continue pour les
 Spécialisé des                                avec  la Chambre d’Artisanat, la Région et la CODEPA.
                             artisans
      Arts
                                               Certification de 340 artisans et artisanes en partenariat
Traditionnels de     Validation des acquis
                                               avec la Chambre d’Artisanat et le Département de la
     Rabat        professionnels des artisans
                                               Formation Professionnelle
                  Programme de l’éducation Réalisation de 50% de modules pour les stagiaires dans
                           financière          le domaine de l’éducation financière

 Concernant les actions prévues pour l’année 2025, elles se présentent comme suit
     Satisfaire les besoins du secteur de l’artisanat en main d’oeuvre qualifiée ;
     Organiser des sessions de formation continue au profit des artisans dans les
     techniques de production et de commercialisation, en partenariat avec la Fondation
     Mohammed V pour la Solidarité ;
     Améliorer la qualité de la formation à travers la certification des artisans dans les
     métiers d’artisanat ;
  ► Poursuivre la formation des stagiaires et des artisans dans le domaine de l’éducation
    financière.

 III.2.3. Instituts et écoles de formation œuvrant dans le domaine de l’agriculture

 Au titre de l’année 2023, les instituts et les écoles de formation relevant du secteur de
 l’agriculture ont assuré des programmes de formation, dont les réalisations et les
 indicateurs y afférents sont résumés dans le tableau ci-dessous :
                                                                                      1Effectif formé
              Etablissement                   Type de formation                                          Taux de
                                                                         Estimation    Réalisation
                                                                                                        réalisation
      Service des Lycées Agricoles            Par apprentissage             7.160         5.846            82%
     Institut Royal des Techniciens                 Techniciens
   Spécialisés en Elevage (IRTSE) de                spécialisés              65             64             98%
                 Fouarat                      Ouvriers qualifiés              15            15            100%
        Institut des Techniciens                Techniciens
                                                                             180           168             93%
   Spécialisés en Mécanique Agricole            spécialisés
    et Equipement Rural (ITSMAER)
                                                    Apprentis                80             55             69%
              de Bouknadel
                                                Techniciens
                                                                             111            111           100%
                                                 spécialisés
    L’Ecole d’Agriculture de Témara
                                                Baccalauréat
                                                                             32             32            100%
                                           professionnel Agricole
                                                Techniciens                  30             26             87%
    Institut Technique Agricole (ITA)
                                             Ouvriers qualifiés              30             17             57%
                 de Tiflet
                                                 Apprentis                   60             48             80%
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME

                                                               |                Effectif formé
           Etablissement               Type de formation                                          Taux de
                                                                   Estimation    Réalisation
                                                                                                 réalisation
                                          Techniciens                 90              81            90%
       ITA de Sahel Boutaher
                                       Par apprentissage              220            218            99%
   Ecole Nationale Forestière des
                                           Ingénieurs                  31            28             90%
         Ingénieurs de Salé

Concernant le premier semestre de l’année 2024, l’état d’avancement de l’exécution du
programme d’action par institut et école se présente comme suit :
                                                                                1Effectif formé
          Etablissement                Type de formation                                           Taux de
                                                                   Estimation     Réalisation
                                                                                                  réalisation
   Service des Lycées Agricoles        Par apprentissage              6.100          2.326            38%
                                          Techniciens                   67             63            94%
         IRTSE de Fouarat
                                       Ouvriers qualifiés               59            49              83%
                                     Techniciens spécialisés           168            158            94%
      ITSMAER de Bouknadel
                                           Apprentis                   80              27            34%
                                     Techniciens spécialisés           107            107            100%
                                          Baccalauréat
  L’Ecole d’Agriculture de Témara                                      18              18            100%
                                     professionnel Agricole
                                           Apprentis                   30             29             97%
                                          Techniciens                  52             48             92%
            ITA de Tiflet              Ouvriers qualifiés              59             54             92%
                                           Apprentis                   60             36             60%
                                     Techniciens spécialisés           60             56             93%
       ITA de Sahel Boutaher              Techniciens                  45             42             93%
                                           Apprentis                  420             227            54%
   Ecole Nationale Forestière des
                                           Ingénieurs                  38             36             95%
         Ingénieurs de Salé

En plus de la poursuite des actions de formation, les actions prévues par ces instituts et
écoles au titre de l’année 2025 s’articuleront principalement autour des axes suivants :
   La poursuite de la construction du centre de Guercif et de Rhamna, le lancement des
   études pour la construction d’un nouveau centre à Boudnib et l’extension de la
   capacité d’accueil et l’équipement de quatre Établissements de Formation
   Professionnelle Agricole (EFPA) relevant du service des Lycées Agricoles ;
► L’équipement d’un amphithéâtre de 264 places au niveau de l’institut des Techniciens
  Spécialisés en Mécanique Agricole et Equipement Rural (ITSMAER) de Bouknadel ;
► L’entretien des bâtiments pédagogiques, l’aménagement et la réparation des
  bâtiments administratifs et des espaces verts, la construction des salles de classe et
  des sanitaires ainsi que la maintenance des installations électriques ;
► L’acquisition du matériel nécessaire pour le bon fonctionnement des instituts.

III.2.4. Instituts dans le domaine de la pêche maritime

Au cours de l’année 2023 et jusqu’au premier semestre de l’année 2024, les principales
actions réalisées par les Instituts de Technologie de la Pêche Maritime (ITPM) d’AI
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


Hoceima, de Safi, de Tan-Tan, de Larache et de Laâyoune et par l’institut Supérieur de
la Pêche Maritime (ISPM) d’Agadir sont récapitulées comme suit :
► L’amélioration de la qualité de la formation assurée par les ITPM, notamment, par le
  renforcement de la formation des techniciens en filière mécanique et capitaine de
  pêche, ainsi que la formation des nouveaux marins de la pêche artisanale dans le
  domaine de la sécurité maritime et dans le domaine de création et de gestion des
  coopératives de pêche ;
► Le renforcement des compétences pratiques des lauréats de la filière mécanique
  pour faciliter leur intégration au marché du travail ;
► L’organisation de formations continues dans les techniques de sécurité et de
  sauvetage ;
► La qualification de la main d’oeuvre pour le secteur de la pêche côtière ;
► La sensibilisation des marins pêcheurs en matière de sécurité maritime, de
  préservation des ressources halieutiques, de création et de gestion des coopératives
  de pêche et de manipulation des instruments de navigation à bord des barques ;
► La diversification des formations dispensées à travers l’introduction de formations
  sur la plongée de loisir et la plongée professionnelle, tout en tenant compte de
  l’approche genre dans les offres de formation ;
► L’acquisition d’un simulateur de conception et de simulation des engins de pêche
  dans le but de renforcer les compétences pratiques des lauréats ;
► L’amélioration du niveau d'accueil des élèves et des usagers de l'institut à travers
  l’entretien et le nettoyage des divers locaux de l’institut, l’entretien et les réparations
  des bâtiments administratifs et la surveillance et le gardiennage de l'institut.
► L’amélioration du niveau d’hébergement des élèves aux instituts ;
► La mise à niveau des structures d’accueil des étudiants en assurant l’entretien des
  blocs sanitaires des internats, des cuisines et des blocs pédagogiques.

Pour l’année 2025, en plus des formations dispensées par les Instituts, les actions
programmées par ces SEGMA portent principalement sur :
   L’organisation de cycles de formation sur la sécurité maritime au profit des nouveaux
   inscrits marins ;
► L’amélioration de la qualité de la formation au profit des marins ;
► L’amélioration du niveau d'hébergement des élèves à l'internat de l'institut ;
► La qualification de la main d’oeuvre dans le secteur de la pêche côtière ;
► La poursuite de l’organisation des campagnes de sensibilisation au profit des marins
  pêcheurs ;
► La mise à niveau des instituts à travers l’acquisition du matériel didactique et
  pédagogique et l’entretien et la réparation du Navire Ecole ;
                          RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► L’acquisition d’un simulateur machine, d’un simulateur de navigation-aquaculture et
  des instruments nautiques ;
► Le développement de conventions de partenariat avec des organismes nationaux et
  étrangers ;
► L’aménagement des salles de formation et l’entretien des locaux des Instituts.

Par ailleurs, l’institut Supérieur d’Études Maritimes (ISEM) de Casablanca a veillé, au
titre de l’année 2023 et du premier semestre de 2024, à l’amélioration des formations
dispensées, notamment à travers :
► L’amélioration de la qualité de la formation à travers la révision complète des
  programmes de formation de l'institut en coopération avec des experts de
  l'organisation Maritime Internationale, le développement de domaines de partenariat
  et de coopération et le recrutement de nouveaux enseignants et du personnel ;
► L’organisation des sessions de formation au profit des cadres et des étudiants de
  l’Académie Maritime de Nouadhibou-Mauritanie ainsi qu’aux entreprises de transport
  maritime et des gens de mer ;
► La mise en place de l’observatoire océanographique comme centre de formation et
  de recherche scientifique dans ce domaine ;
► L’acquisition de matériel pédagogique pour la recherche scientifique ;
► La modernisation des équipements et des infrastructures ;
► Le renouvellement des Certificats de qualité ISO 9001 V 2015.
Au titre de l’année 2025, l’ISEM prévoit une remise à niveau pédagogique de ses futurs
lauréats moyennant :

► Le développement des domaines de partenariat et de coopération et de la recherche
  scientifique ;
► La formation des gens de mer avec la diversification de l'offre dans le domaine de la
  navigation maritime commerciale, des ports et des activités annexes, ainsi que la
  mise en oeuvre de nouvelles filières à l’égard de l’ingénierie électronique navale, la
  licence en hydrographie, le cycle doctoral, etc ;
► Le réaménagement des bâtiments de la direction ;
► La construction du siège de la direction et du centre de conférences ;
► L’organisation de cycles de formation au profit du personnel de l’institut.

III.2.5. Instituts opérant dans le domaine de l’énergie et des mines

Les SEGMA chargés de la formation dans le domaine de l’énergie et des mines sont au
nombre de deux, à savoir l’institut des Mines de Marrakech et l’institut des Mines de
Touissit à Oujda.
Les principales actions entreprises par ces deux SEGMA durant l’année 2023 et le
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


premier semestre de 2024, ont porté essentiellement sur l’amélioration des
prestations rendues aux étudiants, notamment, l’amélioration des conditions
d’apprentissage à travers l’acquisition d’équipements technico-pédagogiques et du
matériel informatique et des logiciels, l’équipement des salles de classe et des ateliers,
la réalisation d'une station de pompage pour alimenter l'internat avec l'eau du puits et
la création des points d'eau RADEEMA et l'aménagement d'un terrain de basketball.
Les actions prévues par ces deux instituts au titre de l’année 2025, s’articulent autour
de l’augmentation de la capacité d’accueil, par le biais du renouvellement et du
renforcement des équipements techniques des ateliers et laboratoires et de
l’acquisition de logiciels spécifiques, l’aménagement et l’entretien de plusieurs locaux,
l’achèvement de la digitalisation de la gestion pédagogique et administrative et l’achat
du matériel informatique ainsi que l’aménagement de postes de gardiennage et de
télésurveillance.

Il1.2.6. Services de formation du personnel et des cadres de l’administration

Ces services, au nombre de sept, ont pour mission principale la conception et la mise en
oeuvre des actions de formation du personnel et des cadres relevant des
départements de tutelle.
Au cours de l’année 2023, la Division des Stratégies de Formation (DSF) relevant du
département chargé de l’éducation nationale a réalisé 705 jours de formation en 195
opérations, au titre desquelles ont participé plus de 7.813 stagiaires, dont plus de 12.377
ont bénéficié du service d’hébergement.
Au titre de l’année 2024 (jusqu’au 28 juin 2024), la DSF a réalisé 393 jours de formation
en 128 opérations et a accueilli plus de 6.780 stagiaires dont 7.787 ont bénéficié du
service d’hébergement.
Ainsi, dans un souci de promouvoir les conditions d’accueil et de travail des bénéficiaires
de ses services, la DSF a réalisé au titre de l’année 2023 et du premier semestre de 2024
plusieurs actions, il s’agit, notamment, de la poursuite de l’exécution des marchés de
nettoyage et de gardiennage, l’exécution d’une convention de droit commun entre la
DSF et le Ministère de tutelle et de contrats de droit commun avec les traiteurs pour
assurer la restauration, la poursuite de l’entretien des espaces verts, ainsi que l’acquisition
de matériel informatique et de toners pour imprimantes.
En plus de la poursuite des actions de formation, les actions prévues par ce SEGMA au
titre de l’année 2025 s’articuleront principalement autour des axes suivants :
► L’élaboration, le lancement et l’exécution du marché d’extension du Centre des
  Formations et des Rencontres Nationales (CFRN) (Hébergement et salles de
  formation) ;
    L’élaboration d’un appel d’offres de la literie et du couchage ;
   L’élaboration d’un appel d’offres de mobilier pour les nouvelles salles dans le cadre
   de l’extension du centre ;
                              RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► La poursuite de l’exécution des marchés de nettoyage et de gardiennage ;
► La conclusion d’une convention de droit commun entre la DSF et le Ministère de
  tutelle concernant la restauration ;
   L’entretien des espaces verts.

En ce qui concerne la Direction du Développement des Compétences et de la
Transformation Digitale (DDCTD) relevant du Ministère de l’intérieur, les réalisations
au titre de l’année 2023 étaient centrées autour de l’accompagnement des
collectivités territoriales en matière de formation, de sensibilisation et de renforcement
des capacités des ressources humaines pour une meilleure gouvernance des affaires
locales. Ces actions se résument dans le tableau suivant :
                             Action                                Indicateur de suivi   Réalisations

 Organisation de séminaires thématiques, de sessions de
 formation et de cycles de perfectionnement et d’intégration          Nombre de
                                                                                           37.000
 en réponse aux besoins et demandes exprimés par les                jours/hommes
 collectivités territoriales en matière de formation.

 Organisation de trois cycles de formation des techniciens
 spécialisés dans les domaines des :
                                                                      Effectif des
      -   Finances locales ;                                                                800
                                                                   stagiaires formés
      -   Espaces verts et développement durable ;
      -   Génie civil : travaux des collectivités territoriales.

 Organisation d’un atelier de formation au profit des élus en        Nombre d’élus
 vue de la promotion de l’intégration de l’approche genre dans       sensibilisés sur        198
 la gouvernance.                                                   l’approche genre

Au titre des exercices 2024 et 2025, les actions programmées s’inscrivent dans la
continuité de la réadaptation aussi bien des offres de formation que des modalités
d’accompagnement et de conseil au service des collectivités territoriales. A ce niveau,
la DDCTD prévoit :
► L’accompagnement des conseils élus des collectivités territoriales, notamment, en ce
  qui concerne le volet relatif au renforcement des compétences ;
► Le renforcement des compétences des cadres moyens des collectivités territoriales
  à travers des formations diplômantes ;
► L’accompagnement des collectivités territoriales en matière d’intégration de
  l’approche genre dans la gouvernance territoriale ;
► La poursuite de la mise en oeuvre des programmes relatifs à l’accompagnement dans
  le domaine de la transformation digitale au niveau des collectivités territoriales
  (Rokhas.ma, Watiqa.ma, chafafiya.ma, chikaya.ma, etc...).
En ce qui concerne la Division Administrative (DA), sous tutelle du Ministère de
l’Economie et des Finances (MEF), elle a réalisé un ensemble d’actions au titre de l’année
2023 et du premier semestre de 2024, portant notamment sur :
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


► La poursuite de la mise en oeuvre du plan de formation dont l’objectif est le
  renforcement des compétences du personnel du MEF ainsi que celles de ses
  partenaires ;
► La réalisation d’un programme de formation sur "la dématérialisation des procédures
  de passation des marchés publics", en collaboration avec les formateurs de la
  Trésorerie Générale du Royaume, au profit des cadres et responsables de la DEPP ;
► L’organisation d’un cycle de formation spécialisée en vue de l’obtention du titre de
  Comptable Agréé, en collaboration avec la Direction des Entreprises Publiques et de
  la Privatisation (DEPP) ;
► L’organisation d’un cycle de formation en anglais professionnel au profit des cadres
  et responsables du MEF.
Par ailleurs, le programme d’action de la DA pour l’année 2025 prévoit la poursuite de
la mise en oeuvre des actions prioritaires, notamment celles relatives à la réalisation
des cycles de formation du personnel du MEF et de ses partenaires inscrits au titre des
marchés-cadre reconduits, ainsi que la consolidation de la coopération avec les
instituts de formation à l’échelle nationale et internationale.
D’un autre côté, le bilan des réalisations, au titre de l’année 2023 et du premier semestre
de 2024 de l’institut de Formation aux Engins et à l’Entretien Routier rattaché au
département de l’équipement a porté sur :

► La formation de 339 conducteurs d’engins des travaux publics relevant des
  collectivités territoriales et des entreprises privées pour le renforcement de leurs
  compétences en matière de maintenance routière ;
► L’exécution de la convention conclue avec la Direction des Routes, à travers la
  formation et la qualification de 30 techniciens et 48 adjoints techniques ;
► Le développement des activités du marketing pour mieux faire connaître l’institut
  auprès des différents organismes publics et privés ;
► La formation et la qualification des techniciens et des adjoints techniques de la
  Direction des Routes dans le cadre de la convention conclue avec ladite Direction ;
   La mise en oeuvre de la convention signée avec l'Agence Japonaise de Coopération
   Internationale ;
   L’amélioration de la gestion du parc engins et véhicules de l’institut ;
► La mise en oeuvre des termes de la convention conclue avec l'Association ANAROUZ
  pour le Génie Rural et le Développement à Azilal en vue d’assurer la formation des
  conducteurs d’engins de travaux publics affiliés à l'association.
Le programme d’action de cet Institut pour l’année 2025 vise en particulier la poursuite
des actions de formation des conducteurs d’engins des travaux publics et des
techniciens de la maintenance routière au profit des collectivités territoriales et des
sociétés privées, la poursuite du développement des activités du marketing pour mieux
faire connaître l’institut auprès des différents organismes, l’amélioration de la gestion du
                            RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


parc des engins de travaux publics et des véhicules lui appartenant , ainsi que le
développement des actions de formation continue dans le cadre des conventions de
partenariat national et international, en particulier avec l'Agence Japonaise de
Coopération Internationale.
Par ailleurs, les principaux projets menés par le Service de la Formation Continue (SFC)
relevant également du département de l’équipement, au titre de l’année 2023 et du
premier semestre de 2024, portent essentiellement sur l’amélioration de la qualité des
services rendus aux clients du Centre d’Accueil et de Conférence (CAC), ainsi que
l’aménagement des espaces verts et l’entretien des locaux.
Au titre de l’année 2025, le service prévoit la poursuite de l’amélioration de la qualité des
prestations rendues aux clients du Centre à travers l’acquisition d'un nouveau groupe
électrogène et l’entretien de ses espaces verts, la maintenance des équipements ainsi
que la promotion des conditions d’accueil et du gardiennage au niveau du Centre.
Quant à l’activité de l’Ecole Nationale de la Santé Publique (ENSP), elle a été
caractérisée par l’organisation du concours d’accès à la formation initiale. Ainsi, 250
candidats ont été admis pour la promotion 2023-2025 du cycle de spécialisation en
santé publique et en management de la santé pour les 4 filières ouvertes : Management
hospitalier, santé de famille et santé communautaire, épidémiologie de santé publique
et gestion des programmes sanitaires. Dans ce cadre, l’Ecole a procédé à la
consolidation du « e-learning » tant pour le volet pédagogique que technique, à travers
une digitalisation des ressources documentaires et une gestion des cours en ligne via
l’application « Moodle ». Dans le même sillage, une formation du corps enseignant a
été assurée.
Par ailleurs, plusieurs projets ont été engagés durant l’année 2023 visant le
renforcement du schéma directeur en informatique et logiciels par l’achat de matériel
et de logiciels, ainsi que l’amélioration de l’accès à la littérature scientifique à travers
la livraison sur demande des documents spécifiques (articles, mémoires) aux
enseignants permanents et aux étudiants.
De plus, au titre du premier semestre de l’année 2024, l’ENSP a réalisé les actions
suivantes :
► Poursuite de l’adaptation du système de formation, y compris le cursus de formation,
  aux exigences des normes pédagogiques et aux évolutions des sciences de la santé ;
► Augmentation des effectifs d’admission pour la formation au niveau de l’école ;
► Adoption de l’approche de médecine de famille, de santé de famille et de la
  communauté ;
► Actualisation et mise en oeuvre de la stratégie sectorielle de la formation continue ;
► Augmentation de la capacité de la formation en médecine de famille et santé
  communautaire, via e-learning ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


► Participation aux séminaires et ateliers sur la migration en partenariat avec
  1’Organisation Internationale de la Migration et ISGIobal Barcelona ;
► Participation à l’étude multicentrique sur les déterminants, les conditions et les
  besoins en santé de la population migrante.
Au titre de l’année 2025, l’ENSP envisage de réaliser le plan d’action suivant :
► Poursuivre l’adaptation du système de formation, y compris le cursus de formation,
  aux exigences des normes pédagogiques et aux évolutions des sciences de la santé ;
► Augmenter les effectifs admis au niveau de l’école ;
► Adopter l’approche de médecine de famille, de santé de famille et de la
  communauté ;
► Actualiser et mettre en oeuvre la « stratégie sectorielle de la formation continue » ;
► Augmenter la capacité de la formation en « médecine de famille et santé
  communautaire », via le e-learning ;
► Lancer et mettre en oeuvre un plan stratégique national « Santé et Immigration ».
Enfin, le plan d’action de la Division de la Formation (DF) relevant du Ministère de
l’inclusion Economique, de la Petite Entreprise, de l’Emploi et des Compétences, au
titre de l’année 2023 et du premier semestre de l’année 2024, a porté essentiellement
sur la poursuite du projet de l’extension de la capacité des structures de la division et
des travaux d’entretien, d’aménagement et de mise à niveau des bâtiments et des
locaux de la Division, le renforcement des compétences et des capacités du personnel
de la division dans les domaines de la gestion financière et de l’ingénierie de la
formation, ainsi que l’amélioration de l’attractivité des prestations de la division. D’un
autre côté, la DF a poursuivi les contacts et les coordinations nécessaires pour la
constitution en son sein d’une équipe pédagogique chargée de la formation et de
l’ingénierie de la formation.
En 2025, la DF envisage la poursuite des travaux d’entretien, d’aménagement et de
mise à niveau des bâtiments et des locaux de la Division, le renforcement des capacités
des ressources humaines dans plusieurs domaines, l’organisation des manifestations
pour promouvoir les prestations de la division, ainsi que la promotion de l’attractivité
des prestations à titre onéreux du SEGMA pour enrichir ses recettes propres.

III.2.7. Instituts de formation dans le domaine des statistiques et des sciences de
         l’information

Au titre de l’année 2023 et du premier semestre de l’année 2024, l’institut National
de Statistique et d’Économie Appliquée (INSEA) relevant du Haut-Commissariat au
Plan (HCP) a réalisé les actions suivantes :
   Formation de 202 lauréats au titre de la promotion 2023 ;
   Formation des ingénieurs d’Etat selon 6 filières pour répondre aux besoins du marché
   du travail ;
                                 RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► Augmentation du nombre d'étudiants inscrits au doctorat ;
► Amélioration de l’état des structures d’accueil des étudiants, notamment en ce qui
  concerne la restauration et l’hébergement.
Pour l’année 2025, le programme d’action de l’INSEA prévoit, en particulier, la
diversification des offres de formation et l’amélioration de leur qualité, l’accroissement
du nombre d’étudiants inscrits au doctorat, ainsi que la poursuite de l’amélioration des
conditions d’accueil des étudiants, notamment la restauration et l’hébergement.

En ce qui concerne l’École des Sciences de l’information (ESI) relevant du HCP, les
réalisations au titre de l’année 2023 et du premier semestre de 2024 se sont articulées
autour des axes suivants :
► Formation de 123 lauréats au titre de la promotion de l’année 2023 ;
► Mise en place d’un système de formation continue profitant au personnel de l’Ecole ;
► Poursuite des travaux de construction d’un internat et d’un restaurant pour les
  étudiants ;
► Mise à niveau de la logistique pédagogique de l’Ecole et équipement des salles, des
  laboratoires et extension de la bibliothèque.
Le programme d’action de l’ESI au titre de l’année 2025 sera dédié à l’amélioration des
conditions de la formation initiale des ingénieurs, de la recherche et de la formation
continue du personnel de l’Ecole, ainsi qu’à l’achèvement des travaux de construction
de l’internat et du restaurant, la mise à niveau de la logistique pédagogique de l’Ecole,
l’achat du matériel informatique et technique et l’acquisition du mobilier des classes et
des laboratoires.

111.2.8. Instituts de formation dans le domaine de l’urbanisme et de l’aménagement du
         territoire

Le tableau ci-après résume les principales actions réalisées par l’institut National de
l’Aménagement et de l’Urbanisme (INAU) au titre de l’année 2023 :
                                                                   Indicateurs                   Taux de
      Objectif                      Actions                                         Estimations
                                                                     de suivi                   Réalisation
                      • Programmation des cours ;              ✓ Achèvement du Tous les           100%
 La poursuite des     • Organisation      des        sorties     programme          semestres
      activités         pédagogiques, des ateliers et des        annuel ;
  courantes des                                                ✓ Nombre         de      10        100%
                        stages pratiques sur le terrain ;
     formations                                                  sorties ;
initiales de l’INAU   • Organisation des soutenances des       ✓ Nombre         de      14        80%
                        Projets de Fin d’Etudes ;                projets soutenus.
                      • Préparation et organisation des        ✓ Réalisation    des
L’organisation du
                        concours d’accès au cycle d’INAU         phases        du        1         90%
concours d’accès
                                                                 déroulé        du
 au cycle d’INAU        (2023-2024).
                                                                 concours.
                      • Organisation des tables rondes,
                                                        ✓ Nombre               des     10         60%
                        conférences et séminaires ;
                                                          activités ;
 Le renforcement      • Organisation des rencontres et
   PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



                                                               Indicateurs                       Taux de
     Objectif                       Actions                                       Estimations
                                                                 de suivi                       Réalisation
    de l’appui         des       voyages       d’échange
 scientifique à la     scientifique avec des universités ✓ Nombre            de       2            0%
    formation          et     écoles     nationales   et   rencontres
                       internationales ;                   d'échange  ;
                      • Organisation des rencontres de
                        sensibilisation et de vulgarisation ✓ Nombre         de       6           50%
                        auprès      des    organismes     et  rencontres.
                        institutions touchant les domaines
                        de       l’urbanisme      et     de
                        l’Aménagement du Territoire.

Le renforcement       • Participation   aux forums   des ✓ Nombre                         4      100%
                                                                             de
du rayonnement          étudiants.                         forums.
  de l’institut


En ce qui concerne les actions mises en oeuvre par l’INAU au titre du premier semestre
de l’année 2024, elles ont porté principalement sur :
    La poursuite des activités de formation dispensées par l’institut au profit des
    étudiants, notamment l’organisation des séminaires, des tables rondes scientifiques,
    des sorties pédagogiques, des voyages d’études, des ateliers et des stages pratiques
    sur le terrain ;
► Le développement des études et de la recherche scientifique, notamment par le
  renforcement du centre d’études doctorales à travers l'ouverture d'une troisième
  promotion du cycle doctoral « Développement territorial, planification et
  gouvernance urbaine », ainsi que la diversification des partenariats avec les
  universités privées et étrangères, en particulier avec les pays anglophones ;
► La requalification du diplôme du Master en Aménagement et en Urbanisme à un
  diplôme d’ingénieur ;
► La promotion de la formation continue dispensée par l’INAU auprès de ses
  partenaires potentiels
► Le développement numérique de l'institut grâce à la mise en place d'une
  infrastructure numérique avancée.
Pour les Ecoles Nationales d’Architecture, les principales réalisations au titre de
l'année 2023 concernent globalement les actions suivantes :

         Objectif________________________ Actions_________________________ Réalisations

    Alignement de la                                               ✓ Suivi continu du contenu des
   formation avec le                                                 cours par la commission
                              Adaptation du contenu des cours avec   pédagogique ;
  contenu du nouveau          le   nouveau    Cahier des   Normes
   Cahier des Normes                                               ✓ Recrutement de nouveaux
                              Pédagogiques Nationales (CNPN) du      enseignants vacataires ;
Pédagogiques Nationales
  dans le domaine de          cycle d’architecte
                                                                   ✓ Renouvellement du contenu
     l'Architecture                                                  de certains cours.
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


         Objectif________________________ Actions_________________________ Réalisations
                           • Développement des relations de
                             proximité avec le milieu socio­
                             économique afin de mieux identifier ✓ Organisation de plusieurs
  Formation continue et      les besoins en matière de formation ;      sessions     de        formation
     renforcement du                                                    continue  au profit   des cadres
   partenariat avec les    • Instauration d’un dispositif de suivi et
                                                                        des sociétés opérant dans le
      universités, les       d’évaluation    de     la    formation
                                                                        domaine de l’immobilier ;
    établissements de        continue ;
                                                                      ✓ Mobilité des étudiants à des
     formation et les      • Encouragement de la mobilité des           écoles     d’Architecture       à
  organismes au niveau
                             étudiants    et   des     enseignants-     l'étranger           (Portugal,
 national et international
                             chercheurs et leur participation à         Espagne, Italie...).
                             plusieurs manifestations scientifiques
                             au niveau du Maroc et de l’étranger.
                                                                        ✓ Optimisation                du
                                                                          fonctionnement              des
                                                                          équipements existants et
                                                                          acquisition    de     nouveau
                                                                          matériel          scientifique,
   Renforcement des
                                                                          didactique et informatique ;
        systèmes
  d'information et de   Aménagement des salles d’étude et ✓ Equipement des ENA en
communication et mise à acquisition du matériel nécessaire   matériels    et    logiciels
       niveau des                                            nécessaires  ;
     infrastructures                                       ✓ Lancement des travaux de
                                                             mise à niveau de 4 salles
                                                             d’étude    avec    structures
                                                             légères     à   l’ENA      de
                                                             Marrakech.

Par ailleurs, les principales actions réalisées par les Ecoles Nationales d’Architecture
au titre du premier semestre de l’année 2024 portent essentiellement sur :
   La poursuite des travaux d’alignement de la formation avec le contenu du CNPN
   concerté entre toutes les Ecoles Nationales d’Architecture, cycle architecte ;
   L’édition de nouveaux numéros de la revue scientifique périodique (AMJAU) ;
   Le renforcement et la mise à niveau de l'infrastructure et des équipements
   pédagogiques des Ecoles ;
   L’équipement de l’ENA de Marrakech par des caméras de surveillance et des
   climatiseurs.
Par ailleurs, les plans d’action de l’INAU et des Ecoles Nationales d’Architecture au titre
de l’année 2025, visent globalement à poursuivre les efforts d’amélioration de la qualité
d’enseignement et d’élargir le champ des formations offertes. Ils sont centrés
particulièrement autour de :
► La validation des textes réglementaires des CNPN cycle architecte et doctorat ;
► L’édition de deux nouveaux numéros de la revue scientifique AMJAU ;
► Le renforcement et la mise à niveau de l'infrastructure et des équipements
  pédagogiques des Ecoles ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


   L’appui scientifique à la formation de l’INAU à travers l’organisation des séminaires
   et des tables rondes scientifiques au profit des étudiants, et la programmation de
   sorties pédagogiques et des voyages d’études ;
   Le renforcement du partenariat et de la coopération entre les Ecoles Nationales
   d'Architecture et les universités, les établissements de formation et les organismes
   spécialisés au niveau national et international ;
   L’optimisation du fonctionnement des équipements existants dans les Ecoles
   Nationales d'Architecture et l’acquisition de nouveaux logiciels et matériels
   scientifiques, didactiques et informatiques en vue d’améliorer la qualité de l’offre
   pédagogique et la performance du système d'enseignement.

111.2.9. Instituts opérant dans le domaine de la communication

Au titre de l’année 2023 et du premier semestre de 2024, les principales opérations
réalisées par l’institut Supérieur de l’information et de la Communication (ISIC) ont
porté sur le lancement des travaux d’aménagement et de revêtements des 2
amphithéâtres et des anciens studios TV et Radio de l’institut, ainsi que sur le
renforcement des moyens logistiques et pédagogiques à travers l’achat de matériel
informatique et technique audiovisuel et l’entretien des bâtiments et des espaces verts.

Le plan d’action de l’ISIC au titre de l’année 2025 prévoit la construction d’un nouveau
bâtiment annexe et la réhabilitation des locaux de l’institut, ainsi que l’équipement des 2
amphithéâtres et des anciens studios TV et Radio.

Quant à l’institut Supérieur des Métiers de l’Audiovisuel et du Cinéma (ISMAC), il a
lancé, durant l’année 2023 et le premier semestre de 2024, plusieurs projets structurants
pour assurer une meilleure prestation de services au profit de ses étudiants selon les
normes internationales dans le domaine. A cet effet, les chantiers marquants de cette
période se sont concentrés autour du développement de l'infrastructure de l'institut à
travers un ensemble de projets portant principalement sur :

► Le lancement des travaux de construction d’une extension de l’ISMAC dédiée au
  Centre d’étude et de recherche à l’avenir de l’image ;
► Le traitement acoustique pour l’amélioration des performances d’isolation phonique
  et de sonorisation ;
► L’acquisition de fourniture, installation et mise en service des équipements
  audiovisuels et de sonorisations ;
► L’aménagement et l’équipement d’une salle de conférence polyvalente.

Par ailleurs, au titre de l’année 2025, l’ISMAC prévoit la mise en place des projets visant,
d’une part, l’accompagnement des étudiants en matière de formation et d’autre part,
l’amélioration des infrastructures pédagogiques. A cet effet, l’ISMAC a mis en place un
plan retraçant les principales actions à réaliser l’année prochaine, notamment :
                          RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► La mise en place d’un raid d’archivage ;
► Le lancement des travaux de construction d’un centre d’étude et de recherche dans
  l’avenir de l’image ;
► La fourniture et l’installation des équipements techniques et pédagogiques pour le
  centre d’étude et de recherche dans l’avenir de l’image ;
► La fourniture de mobilier et de matériels pour le centre d’étude et de recherche dans
  l’avenir de l’image ;
► Le développement d’une Médiathèque pluridisciplinaire liée avec tous les locaux de
  l’ISMAC par internet ;
► La création de partenariats avec le secteur public et privé pour le renforcement des
  compétences des étudiants dans le domaine du cinéma et de l’audiovisuel.

Il1.2.10. Institut Royal de Formation des Cadres de la Jeunesse et des Sports

Au titre de l’exercice 2025, l’institut Royal de Formation des Cadres de la Jeunesse
et des Sports (IRFC) envisage la réalisation des actions suivantes :
► La digitalisation des services de l’institut à travers la mise en place d’un système
  d’information répondant aux exigences d’efficience, d’efficacité et de bonne
  gouvernance ;
► La rationalisation des dépenses liées à l’entretien des véhicules devenus vétustes et
  l’acquisition d’un minibus pour assurer le transport des étudiants et du personnel ;
► La pérennisation du rayonnement de l’IRFC et la confirmation de son positionnement
  en tant que référence de la formation et de la recherche dans les domaines du sport
  et de la jeunesse ;
► La valorisation des revues scientifiques des chercheurs (participation à des congrès
  et publication d’articles scientifiques) ;
► La mise à jour de l’organigramme de l’institut ;
► L’aménagement et l’équipement de la cuisine et de la buanderie du centre Moulay
  Rachid.

111.3. Domaine des activités récréatives

Il1.3.1. Complexe Moulay Rachid de la Jeunesse et de l’Enfance de Bouznika

En plus des opérations courantes de gardiennage, de surveillance, de nettoyage et de
restauration, le Complexe Moulay Rachid de la Jeunesse et de l’Enfance a été mis à
la disposition des citoyens au titre de l’année 2023 et du premier semestre de 2024,
afin d’accueillir un grand nombre de bénéficiaires. De nombreuses actions ont été ainsi
réalisées pour l’amélioration des conditions d’accueil, notamment les travaux
d’entretien, de maintenance des bâtiments, d’installation et d’équipement des réseaux
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


du Complexe, de réhabilitation des espaces verts, d’aménagement des espaces
sportifs, ainsi que la création des moyens de communication (site Web, page
Facebook, dépliants...).
Par ailleurs, au titre de l’année 2025, le Complexe Moulay Rachid de la Jeunesse et de
l’Enfance envisage le réaménagement et la réhabilitation des bâtiments
d’hébergement en procédant à la rénovation de la literie et des équipements,
l’aménagement des vestiaires et d’un bloc sanitaire pour les terrains de sport, la mise
en oeuvre des travaux d’éclairage des terrains, l’aménagement d’un parcours sportif
avec des espaces d’entrainement et des bancs de jardin, ainsi que l’entretien et la
maintenance des bâtiments et équipements techniques du complexe.

III.3.2. Service du Contrôle des Etablissements et des Salles Sportives

Au titre de l’année 2023 et du premier semestre de 2024, le Service du Contrôle des
Etablissements et des Salles Sportives a lancé plusieurs projets structurants pour
assurer une meilleure prestation de services au profit des adhérents. A cet effet, les
chantiers marquants de cette période se sont concentrés autour des actions
suivantes :
   L’amélioration de la qualité de ses prestations ;
   La mise à niveau des piscines ;
► L’ouverture de la piscine de M’diq ;
► L’acquisition du          matériel      informatique   et   bureautique   pour   les   piscines
  opérationnelles ;
► L’acquisition des équipements sportifs.

En ce qui concerne l’année 2025, le service projette l’ouverture des piscines achevées.
Il prévoit également l’installation des pompes à chaleur à la piscine d’EL Jadida, ainsi
que l’aménagement des piscines de Larache, Berkane, Tan-Tan et Martil.

111.3.3. Musée Mohammed VI pour la civilisation de l’eau au Maroc

Le Musée Mohammed VI pour la civilisation de l’eau au Maroc a connu une année
budgétaire 2023 très dynamique et un déploiement de plusieurs nouvelles actions, à
savoir :
► Le développement de programmes et d’activités destinés aux institutions scolaires
  et culturelles ;
► La poursuite de la sensibilisation des citoyens sur la rationalisation de la
  consommation de l’eau ;
   La contribution dans la politique nationale relative à la gestion des ressources
   hydriques ;
                                    RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


        L’accroissement des ventes des tickets en raison de l’organisation des tournées
        promotionnelles auprès des agences de voyages et des institutions hôtelières au
        niveau local ;
        L’organisation de la 4ème édition du concours international "Eau que nous voulons"
        en coordination avec le Réseau Mondial des Musées de l’Eau ;
    ► Le renforcement de l’échange culturel, éducatif et intellectuel avec les différentes
      régions et les cultures du monde ;
    ► L’initiation de la mise en place d'une méthodologie de coopération avec les
      institutions culturelles et artistiques nationales et internationales afin de contribuer à
      la préservation du patrimoine culturel de l'eau et de bénéficier des expériences des
      musées de l'eau dans le monde ;
    ► La programmation régulière des travaux pratiques au profit des jeunes en vue de les
      intégrer dans les programmes de l’éducation et de la sensibilisation autour des
      différents volets en relation avec le sujet de l’eau.
    Le tableau ci-dessous récapitule les principales actions réalisées par le Musée
    Mohammed VI pour la civilisation de l’eau au Maroc au titre de l’année 2023 :
                                                                      Indicateur       Réalisations      Taux de
      Objectif                     Mesures prises
                                                                       de suivi                         réalisation
Développement des ✓ Location de la salle polyvalente pour        ✓ Fréquence de          42 fois dans      50%
      ressources        les différentes activités culturelles et   location de la           l’année
   financières du       scientifiques.                             salle ;
       Musée et       ✓ Renforcement de l’attractivité du        ✓ Nombre        de         25.045        70%
 sensibilisation des    Musée      auprès des jeunes        en     visiteurs ;            visiteurs
  jeunes aux défis      particulier par le biais de la           ✓ Valeur totale
    futurs liés à la    communication avec les associations        des ressources          819.485         62%
 rationalisation de     de la société civile et les institutions   financières             dirhams
         l’eau          scolaires publiques ou privées.            générées.
                     ✓ Installation des panneaux verticaux       ✓ Nombre         de       12.774         70%
                         dans des sites historiques et des          visiteurs ;           visiteurs
                         musées à Marrakech.
   Présentation du    ✓ Contact direct avec des guides ✓ Nombre                       60 agences          64%
  musée au niveau       touristiques ;                             d’agences      de
        national
                                                                   voyage ;
                      ✓ Invitation et accueil des délégations.                       16 délégations       50%
                                                                 ✓ Nombre         de
                                                                   délégations.
                      ✓ Organisation de la quatrième édition ✓ Nombre
   Présentation du
                        du concours international "Eau que                                  200
  musée au niveau                                                  d’institutions                         70%
                        nous voulons” en coordination avec le                          institutions
     international                                                 participantes
                        Réseau mondial des musées de l’eau.

    Durant le premier semestre de l’année 2024, les actions majeures réalisées par le
    Musée Mohammed VI pour la civilisation de l’eau visent essentiellement la poursuite
    des efforts pour la sensibilisation des jeunes autour de la pénurie d’eau et la
    consolidation de l’engagement durable pour la préservation et la rationalisation de
    l’utilisation des ressources hydriques, ainsi que le partage et l’échange des expériences
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


en matière de gestion de l’eau afin de tirer les enseignements et de s’aligner sur les
meilleures pratiques. Les principales actions effectuées se résument comme suit :

► Le renforcement de l’attractivité du musée afin d’augmenter le nombre des visiteurs
  de différentes catégories, notamment les jeunes à travers la communication avec les
  associations de la société civile et les institutions scolaires publiques ou privées ;
► La location de la salle polyvalente pour les différentes activités culturelles et
  scientifiques ;
► La mise en place d’une stratégie promotionnelle du musée en vue d’augmenter la
  part des visiteurs, particulièrement les touristes marocains et étrangers ;
► La participation du musée dans des évènements culturels et scientifiques au niveau
  national ;
► L’organisation des visites guidées au profit des délégations officielles ;
► La mise en place du programme pédagogique au profit des institutions scolaires et
  universitaires ;
► La présentation du musée dans les médias aussi bien au niveau national
  qu’international ;
► L’organisation des concours mondiaux au niveau national pour la sensibilisation sur
  l’importance de l’eau ;
► La création de partenariats avec plusieurs institutions.

S’inscrivant dans une démarche d’amélioration continue des prestations rendues aux
usagers, le plan d’action prévu au titre de l’année 2025 est articulé autour des points
suivants :

► La contribution dans la sensibilisation des citoyens autour de la problématique de
  l’eau ;
► L’amélioration des ressources financières du musée ;
► L’organisation des activités du musée au niveau régional, national et international ;
► Le renforcement de la communication numérique, à travers des actions de promotion
  du musée sur les réseaux sociaux et la réactivation de son site internet.

111.4. Domaine des autres actions sociales

111.4.1. Division du Pèlerinage

Grâce à la bonne convergence et les efforts déployés par tous les secteurs nationaux
impliqués dans le processus, le Ministère des Habous et des Affaires Islamiques a réussi
à organiser la saison du Hajj de l'année 2023, malgré les difficultés liées au retard du
programme des vols de la compagnie aérienne saoudienne et la non-approbation d'un
certain nombre de vols de la Royal Air Maroc par l'Autorité d'aviation civile saoudienne,
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


en plus du retard des autorités saoudiennes dans l'annonce de l'organisation du Hajj qui
n'a pas laissé suffisamment du temps pour tenir les réunions nécessaires avec les
différentes parties impliquées dans l'organisation du Hajj.
De nombreuses mesures ont été prises en vue d’assurer le bon déroulement du
pèlerinage au titre de l’année 2023, à savoir :
► La référence au quota agréé au Royaume du Maroc qui est de 34.000 pèlerins sans
   condition d'âge ;
► La sélection des listes des citoyens qui effectueront le rituel Hajj parmi ceux qui ont
  été reportés de la saison dernière (2022) en raison du fait qu'ils ne remplissent pas la
  condition d'âge exigée ou de vaccination contre le Corona virus, et ce conformément
  à la décision de la commission royale du pèlerinage et en complétant les listes
  d'attente issues du tirage au sort de 2019 pour les deux listes (Habous et Agence de
  voyage) ;
► La fixation des frais du pèlerinage à 62.929,00 dirhams ;
► La création de l'application électronique "Massar Al Hajj " dans le but de l'utiliser à
  toutes les étapes du Hajj et de suivre aussi le chemin des pèlerins en scannant le code
  QR créé sur les nouvelles cartes préparées pour les pèlerins ;
► La conclusion d’un marché portant sur l'achat des pochettes au profit des pèlerins
  pour un montant de 374.400,00 dirhams ;
► La conclusion d’un marché portant sur l'achat des étiquettes pour bagages d’un
  montant de 180.000,00 dirhams ;
► L’instauration de l'application "Dalil Al Hadj" sur les plateformes "Play Store" et "App
  Store" pour un montant de 84.000,00 dirhams. Cette application comprend une
  explication détaillée des rituels Hajj en arabe et en différentes langues nationales
  (Tachalhit, Tarifit et Tamazight) en plus d'une vidéo qui comprend des conseils
  importants pour les pèlerins.
Par ailleurs, durant le premier semestre de l’année 2024, les principales décisions
prises sont résumées comme suit :
► La fixation du prix du billet d'avion pour les pèlerins de l'organisation officielle à
    12.400,00 dirhams TTC, et pour les membres de la délégation marocaine à 10.000,00
    dirhams TTC ;
► La fixation des frais du pèlerinage à hauteur de 66.865,50 dirhams ;
► Le début du processus de paiement des frais du pèlerinage en une seule tranche du
  22 au 31 janvier 2024 ;
► L’organisation de séminaires de formation et de réunions de communication avec les
  délégués régionaux et provinciaux et les accompagnateurs des pèlerins, d'un coût
  d'environ 349.032,00 Dhs.
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


Ainsi, pour améliorer le fonctionnement de la délégation et développer les services
offerts aux pèlerins, les actions suivantes ont été menées
► L’amélioration de l'encadrement et de l'accompagnement des futurs pèlerins en
  affectant un encadrant pour chaque groupe d'environ 48 pèlerins ;
► La mise en place d'une nouvelle structure pour les différentes délégations
  marocaines (administrative, sanitaire, scientifique, etc.) afin de déterminer avec
  précision la composition et les missions de chacune ;
► Le développement du programme électronique "Massar Al Hajj" qui permet de suivre
  toutes les étapes parcourues par le pèlerin lors du Hajj ;
► L’amélioration des services offerts aux pèlerins aux lieux saints en établissant un
  cahier des charges précis à cet égard, en optant notamment pour l'utilisation de la
  surveillance électronique pour garantir que tous les pèlerins bénéficient des repas.
Quant à l’année 2025, l’opération d’inscription a été ouverte aux personnes souhaitant
participer au tirage au sort du pèlerinage 1446/2025 par voie électronique du 05 au 16
février 2024. L’opération du tirage au sort sera effectuée ultérieurement.

111.4.2. Service des Unités de Formation Artistique et Artisanale

Au titre de l’année 2023, le Service des Unités de Formation Artistique et Artisanale
(SUFAA) a poursuivi ses missions articulées autour de l’amélioration des conditions de
la réinsertion sociale et économique des détenus après leur libération. Ainsi, en ce qui
concerne la production agricole, la succession des années de sécheresse a été la cause
directe de la réduction des réalisations au niveau de la production agricole et de la mise
en jachère des terres. Le SUFAA a pu réaliser son programme pour l’année 2023, en
réalisant la mise en jachère des sols et la culture de 185 hectares dans le cadre de la
campagne agricole 2022/2023. De plus, le SUFAA a procédé à la vente des récoltes
agricoles aux enchères publiques et à l’achat de semences de qualité.
S’agissant de la production animale, le Service a poursuivi son programme d’élevage du
cheptel à travers la vaccination de bétails, l’acquisition d’aliments et de foin, l’organisation
des visites périodiques des vétérinaires, ainsi que la vente de béliers à l’occasion de l’Aïd
Al-Adha 1444 Hijriya.
Par ailleurs, en matière de production artistique et artisanale, le SUFAA a pu renforcer et
diversifier les unités de formation artistique et artisanale pour en faire un outil de
réinsertion des détenus, notamment à travers le démarrage de la production de la tenue
pénale au sein des unités de formation, la création de nouvelles unités de production, le
lancement d’un projet de plateforme de vente en ligne, en plus de l’organisation des
expositions de promotion des produits.
Durant le premier semestre de l’année 2024, le SUFAA a décidé d’annuler le
programme de la campagne agricole 2023/2024 sur la base des prévisions
pluviométriques et suite aux mauvaises réalisations enregistrées durant les années
précédentes dues à la sécheresse. Quant à la production animale, le programme de
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


travail pour le premier semestre 2024 est achevé à hauteur de 50% notamment en ce
qui concerne la programmation de la reproduction du bétail semestriellement, la vente
aux enchères publiques d’un certain nombre de bétail et l’acquisition de nouveaux
géniteurs pour le renouvellement du cheptel. De plus, le Service a procédé, dans le
cadre de la production artisanale et artistique, au renforcement et à la diversification
des unités de formation artisanale et artistique en vue de les rendre un outil de
réhabilitation et de réinsertion des détenus.
Par ailleurs, au titre du plan d’action de l’année 2025, le SEGMA prévoit, sur le plan de
la production agricole, l’exploitation de 280 hectares de terres cultivables, visant ainsi
l’atteinte d’un taux d’exploitation de 70%. Pour la production animale, le SUFAA
envisage la programmation de la reproduction du bétail semestriellement, et
l’engraissement et la vente des moutons à l'occasion de l'Aïd al-Adha pour l'année
1446 du calendrier Hijri. S’agissant de la production artisanale et artistique, le Service
envisage de lancer le programme de prisons productives dans divers établissements
pénitentiaires, de développer un système de suivi des unités de formation afin
d’augmenter les performances aussi bien en quantité qu’en qualité, et de mettre à jour
la base des données des produits artistiques et artisanaux.

Il1.4.3. Direction des Affaires Consulaires et Sociales

Au titre de l’année 2023, les principales actions réalisées par la Direction des Affaires
Consulaires et Sociales (DACS), visant l’amélioration de la qualité des services
consulaires et les conditions d’accueil, sont résumées comme suit :
► La mise en place du registre électronique centralisé des « Prestations consulaires de
  proximité », qui permet aux MRE de demander des prestations consulaires auprès de
  toutes les Missions Diplomatiques et Postes Consulaires MDPC, indépendamment de
  leurs postes de rattachement ;
► La généralisation du système électronique de prise de rendez-vous ;
► La contribution à la réussite de l’opération « Marhaba 2023 » ;
► La poursuite de la numérisation des actes d'état civil par les missions diplomatiques
  et les postes consulaires avec l'aide d'agents vacataires ;
► L’organisation de consulats mobiles et de journées portes ouvertes pendant les
  week-ends et les jours fériés dans les pays d’accréditation dans le cadre du
  rapprochement de l'administration des citoyens.
Durant le premier semestre de l’année 2024, les réalisations de la Direction des Affaires
Consulaires et Sociales ont porté essentiellement sur la mise à jour et la révision de
certains contrats afférents à la sécurité, au nettoyage et au gardiennage, la supervision
du fonctionnement du centre d’appel consulaire par l’engagement des dépenses
contractuelles, le suivi de la numérisation des actes d’état civil avec l’aide d’agents
vacataires, ainsi que la généralisation de la dématérialisation des timbres à travers le
système « eTimbre ».
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


Au titre de l’année 2025, la DACS prévoit la réalisation des actions ci-après
► La mise à jour et la révision de certains contrats liés à la sécurité, au gardiennage et
  au nettoyage au niveau des postes consulaires ;
► La numérisation des actes d’état civil et leur intégration au niveau du système e-
  Zdiyad ;
► La mise à disposition de moyens matériels et logistiques pour l’organisation de
  consulats mobiles ;
► La mise en oeuvre du programme « Watiqa.ma » concernant les actes d'état civil et
  le certificat d'immatriculation consulaire ;
► Le renforcement des postes consulaires par les moyens humains et matériels
  nécessaires à la réussite de l’opération « Marhaba 2025 » ;
► La mise en oeuvre du système électronique intégré « e-Consulat », qui permet la
  délivrance à distance de quatre prestations consulaires, à savoir : l’immatriculation
  consulaire à distance, l’autorisation des transferts des corps, l’authentification des
  permis de conduire, ainsi que la gestion des plis de justice.

III.5. Domaine des pouvoirs publics et services généraux

Il1.5.1. SEGMA de la Trésorerie Générale du Royaume

Le bilan des réalisations de la Trésorerie Générale du Royaume (TGR) au titre de
l’année 2023 et du 1er semestre 2024 a porté essentiellement sur l’aménagement et la
réhabilitation de plusieurs trésoreries et perceptions dont celles d’el Aioun sidi Mellouk,
Kénitra, Guercif, Mechraa Belksiri, Benguerir et Bouskoura, ainsi que le développement
des systèmes d’information à travers, notamment, la mise en oeuvre d’un système de
management de la sûreté et de la sécurité au sein de la TGR.
Par ailleurs, la TGR prévoit au titre de l’année 2025 le lancement des travaux
d’aménagement des locaux de certaines trésoreries dans le cadre du programme
pluriannuel des aménagements, l’acquisition et la mise en service d’équipements
informatiques, ainsi que l’achat de prestations d'assistance technique pour la
maintenance des logiciels et des équipements informatiques dédiés aux serveurs de
bases de données.

111.5.2. Administration des Douanes et Impôts Indirects

En ce qui concerne l’Administration des Douanes et Impôts Indirects (ADII), les
principales actions réalisées au titre des années 2023 et 2024 (jusqu'au mois de Mai)
ont été centrées autour de l’amélioration des conditions de travail et d’accueil des
usagers, la simplification des échanges et la lutte contre la fraude. Ceci s’est traduit
notamment à travers :
► L’achèvement des travaux de construction du siège de la direction provinciale d'AI-
  Hoceima ;
                            RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


   L’acquisition et l’installation du matériel technique et du mobilier de bureau destinés
   aux différents services de l’ADII ;
► La mise en place pour le compte de l’Administration des Douanes et Impôts Indirects
  d’une solution monétique intégrée et centralisée pour le paiement par terminal
  électronique (TPE) des créances douanières ;
► L’acquisition, l’installation et la mise en œuvre d’équipements électroniques.
Au titre de l’année 2025, les actions programmées par l’ADII visent principalement la
poursuite des efforts portant sur l’amélioration des conditions de travail et d’accueil
des usagers et la simplification des échanges, à travers la réalisation de plusieurs
études d’aménagement, et le lancement de travaux d’aménagement et d’installation
de ses locaux, l’acquisition de mobilier de bureau, d’outils informatiques et de logiciels
appropriés, ainsi que la modernisation des systèmes d’information.

111.5.3. Direction de l’imprimerie Officielle

Au cours de l’année 2023, la Direction de l’imprimerie Officielle (DIO) a poursuivi ses
efforts visant l’amélioration des travaux d’impression des éditions du Bulletin Officiel
du Royaume et la formulation des principaux textes législatifs et règlementaires dans
le cadre de la série "Documentation juridique marocaine", à travers l’acquisition de
papier édition satiné en bobines, l’achat de différentes fournitures et produits
d'impression, ainsi que l’acquisition de matériels informatiques et de logiciels
spécialisés.
La DIO a procédé également, pendant la même année, à la réalisation de divers travaux
de renforcement des fondations de la Direction, l’entretien, à la réparation et à la
maintenance des machines d’impression numériques, ainsi que l’entretien et le
nettoyage des locaux de la DIO.
Quant au premier semestre de l’année 2024, la DIO a réalisé des travaux divers se
rapportant notamment à l’aménagement et à la réfection des locaux, le réseau
électrique, le monte-charge, et l’entretien et la réparation du matériel d’imprimerie.
Au titre de l’année 2025, le programme d’action de la DIO s’inscrivant dans le cadre
de la poursuite du chantier de mise à niveau et de rationalisation de la gestion de
l’imprimerie Officielle, s’articule autour des axes suivants :
► L’amélioration de l’accès aux programmes de formation, conférences et séminaires
  organisés à l’intérieur et à l’extérieur du Royaume ayant pour objectif la promotion
  de l’utilisation des technologies d’information et de communication dans les
  domaines de l’édition et de l’impression numérique ;
► La poursuite de la réalisation de l’étude relative à la préparation des cahiers des
  prescriptions spéciales et des règlements de consultation pour acquérir de nouvelles
  machines d’impression permettant de s’adapter à l’impression numérique ;
► La numérisation et la mise en ligne du contenu du Bulletin Officiel du Royaume ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


   L’adoption de l’archivage électronique pour répondre aux enjeux liés au cycle de vie
   des documents juridiques, et la définition d’une méthodologie pour le mettre en place
   en s’appuyant sur une feuille de normes et de gestion dans la durée ;
   Le maintien du processus de généralisation de l’utilisation du portail électronique
   relatif au dépôt et à la publication des annonces pour englober également les
   annonces judiciaires et administratives, visant leur numérisation globale, et la
   simplification du processus de recouvrement des créances y afférentes ;
   La mise en place d’un moteur de recherche relatif aux annonces légales au niveau du
   site électronique, tout en offrant la possibilité de leur téléchargement.

111.5.4. Centre Royal de Télédétection Spatiale

Les principales actions menées, ou en cours d’exécution, par le Centre Royal de
Télédétection Spatiale (CRTS) au titre du premier semestre de l’année 2024 se
présentent comme suit :
► La signature des conventions, avec les directions régionales de l’équipement et du
  transport, de la logistique et de l’eau, de Salé-Kénitra et Dakhla Oued Eddahab ;
► L’exécution des conventions avec les directions régionales de l’équipement et du
  transport, de la logistique et de l’eau, de Casablanca-Settat, Marrakech-Safi, Tétouan-
  Al-Hoceima, Souss-Massa, l’Oriental, Laâyoune-Sakia El Hamra, et Guelmim-Oued
  Noun ;
   La mise en place d’un outil de modélisation du risque de tsunami au Maroc, en
   partenariat avec le Fonds de Lutte contre les Catastrophes Naturelles ;
► La mise en place d’une plateforme « Géoportail » d’échanges de données maritimes
  multithématiques produites par les différents acteurs du comité national de
  coordination dans les domaines de l’hydrographie, de l’Océanographie et de la
  cartographie Marine ;
► La poursuite du programme de formation continue en télédétection spatiale et
  système d'information géographique (SIG) destiné aux utilisateurs nationaux ;
► L’organisation d’un atelier de sensibilisation sur les technologies spatiales au service
  de la gestion des risques naturels, au profit des acteurs nationaux impliqués dans la
  gestion des risques naturels ;
► Le renforcement des capacités des cadres et du personnel du CRTS à travers
  l’organisation de plusieurs formations techniques.
Par ailleurs, et au titre de l’année 2025, le Centre prévoit la réalisation des actions ci
dessous :

► L’acquisition des images satellites selon les besoins définis ;
► L’acquisition de logiciels et de matériel informatique pour le stockage et le traitement
  des données satellitaires ;
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► La maintenance et la réparation de matériel informatique et électrique ;
► La poursuite du programme de formation continue et de séminaires destinés aux
  utilisateurs nationaux.

111.5.5. Imprimerie Dar Al Manahil

Au titre de l’année 2023 et du premier semestre de l’année 2024, l’imprimerie Dar Al
Manahil a poursuivi ses travaux d’impression et de tirage pour répondre aux besoins
des usagers et de son ministère de tutelle, le Ministère de la Jeunesse, de la Culture et
de la Communication (MJCC), en termes de documents. Ces documents sont répartis
en plusieurs séries (rapports, catalogues, revues, invitations, autocollants, affiches,
documents administratifs,...). Les travaux réalisés dans ce sens sont présentés comme
suit :
                                                       Réalisations         Réalisations
                                 Action : type de
           Objectif                                       2023             à fin juin 2024
                                   publication
                                                    (Nombre de copies)   (Nombre de copies)
 Répondre aux besoins du MJCC         Livres              5.902                  1.350
 en termes d’impression et de
                                   Documents              37.327               26.828
 tirage
 Rendre    aux    usagers  des        Livres              11.030               15.250
 services de qualité moyennant
                                   Documents              2.040                 300
 une rémunération

Par ailleurs, ce SEGMA prévoit, au titre de l’année 2025, la formation des cadres
techniques et administratifs spécialisés, et la modernisation des outils de travail afin
d’accompagner le développement qui marque le domaine de l’impression et de la
conception, ainsi que l’entretien du matériel technique existant.

Il1.5.6. Centre National de la Documentation

Au titre de l’année 2023 et du premier semestre de l’année 2024, le Centre National
de la Documentation (CND) a poursuivi ses actions en s’inscrivant dans une logique
de renforcement de ses activités informationnelles et d’amélioration de sa capacité de
communication avec son environnement. Les principales actions réalisées sont les
suivantes :
► La gestion du projet Abhatoo-Nouvelle génération avec le prestataire (suivi des
    livrables et coordination avec les différents intervenants du projet) ;
► L’achèvement de l'exécution de l’étude relative au projet Abhatoo-Nouvelle
  Génération et la finalisation des livrables ;
► Le développement de la partie Front Office du portail “Abhatoo” et son intégration
  dans les documents de l’appel d’offre du projet d’acquisition d’une nouvelle
  plateforme du portail ;
► L’acquisition d’une nouvelle solution de sécurité informatique pour le CND, son
  exploitation et suivi de son bon fonctionnement ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


   L’élaboration d’un benchmark sur les logiciels de gestion des portails documentaires
   utilisant des moteurs de recherche en recensant leurs meilleures fonctionnalités à
   offrir aux usagers et leur intégration ou non de technologies d'intelligence artificielle ;
   La mise à niveau des ressources humaines du Centre National de la Documentation,
   à travers l’organisation de plusieurs sessions de formation au profit du personnel ;
En ce qui concerne l’année 2025, le programme d’action du CND s’articule autour des
axes ci-dessous :
   L’amélioration de l’intégration des objectifs du développement durable dans le
   périmètre de collecte, de traitement, de recherche documentaire et de veille ;
► L’encadrement des directions régionales pour la délégation des activités de collecte,
  traitement et diffusion documentaires et de veille, et ce, dans le cadre de la mise en
  oeuvre de la déconcentration administrative du HCP ;
► La révision du rôle du « comité scientifique de sélection des documents » dans sa
  relation avec les nouveaux systèmes de gestion documentaire en cours de mise en
  oeuvre ;
► Le renforcement de l’introduction des Nouvelles Technologies de l’information ;
► L’élargissement du champ de recherche à travers l’abonnement à de nouvelles bases
  de données étrangères, principalement textuelles ;
► La refonte du portail « Abhatoo » afin d’améliorer son potentiel de production
  documentaire et de contrôle technique de la qualité de ses entrées et de suivi des
  recherches effectuées ;
► La révision du rôle et des modes de fonctionnement du « comité scientifique de
  sélection des documents » dans sa relation avec les nouveaux systèmes de gestion
  documentaire en cours de mise en œuvre, en l'occurrence les applications du dépôt
  institutionnel électronique des documents et du portail Abhatoo-Nouvelle
  génération ;
► La mise en place d’une stratégie d’archivage électronique et physique des
  documents administratifs et financiers (objectif de numériser 10.000 nouveaux
  documents en 2025) ;
► Le renforcement du réseau de communication entre le CND et les différentes
  institutions nationales productrices des documents
► La programmation d’un plan de formation pour la mise à niveau du personnel dans
  les différents domaines

111.5.7. Centre de Publication et de Documentation Judiciaire de la Cour de Cassation

Les actions menées pendant l’année 2023 par le Centre de Publication et de Documentation
Judiciaire de la Cour de Cassation (CPDJ) ont permis l’enrichissement du casier de la Cour, à
travers la publication des textes de lois et autres documents judiciaires, sur supports
électroniques et papiers. Il s’agit des cahiers de la Cour de Cassation consistant en la
                            RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


publication des décisions émises aux communes soulaliyates, et l’édition des revues
spécialisées publiant une sélection des diverses décisions prises par les différentes
chambres de la cour.
Par ailleurs, les actions réalisées au titre du premier semestre de l’année 2024 ont porté
principalement sur l’édition de plusieurs revues spécialisées de la Cour de Cassation
relatives aux arrêts des différentes chambres, ainsi que la réalisation des dossiers
documentaires périodiques pour répondre aux demandes des conseillers visant à mener
des recherches sur des sujets de pertinence juridique ou judiciaire en investissant dans
le solde documentaire disponible audit centre.
Le programme d’action du CPDJ pour l’année 2025, prévoit, en particulier, la préparation
des revues spécialisées de la Cour de Cassation contenant une sélection des décisions
émises par les différentes chambres de la Cour de Cassation et la publication des cahiers
relatifs à la lutte contre la violence à l’égard des femmes et à la fiscalité sur les terrains
non bâtis, ainsi que l’édition du rapport annuel de l’année 2024.

111.5.8. Unité de Fabrication de Masques de la Gendarmerie Royale

Au titre de l’année 2023, les recettes générées de la vente de 5.159.600 masques FFP2
ont enregistré un montant de 11.917.960 dirhams. Par ailleurs, l’Unité de Fabrication de
Masques de la Gendarmerie Royale (UFM) a oeuvré à la satisfaction des demandes en
masques chirurgicaux exprimées par les administrations publiques et le secteur privé et
a réalisé, dans ce sens, des ventes de l’ordre de 1.147.400 masques rapportant des
recettes s’élevant à 1.800.630 dirhams.

Au titre du premier semestre de l’année 2024, l’UFM a procédé à l'exécution des
différents programmes prévus pour l'entretien, la maintenance et le développement des
multiples équipements de l'Unité. Une nouvelle usine est en cours de construction, ce qui
permettra dans le court et moyen terme de diversifier la palette des produits de l'UFM
et surtout d’augmenter de manière significative la capacité de production. D’autre part,
l'UFM poursuit la satisfaction des demandes des masques FFP2 ou chirurgicaux par la
conclusion de plusieurs conventions et contrats de droit commun avec les différentes
administrations publiques et organismes privés du Royaume.

Par ailleurs, il est à signaler que le programme d’action de l’UFM au titre de l’année
2025, s’inscrit dans le cadre de la poursuite des travaux entamés en 2024. Il porte
essentiellement sur la finalisation du projet de transfert des équipements de la
Protection Civile de Sidi Allai Bahraoui vers l’usine de l’UFM à Benslimane, la
diversification de la gamme des produits en équipant la nouvelle usine en cours de
construction par des machines de nouvelle génération, le renforcement du contrôle
qualité en poursuivant les efforts d’entretien et de maintenance des équipements de
production, la satisfaction de la demande en masques exprimée par le Ministère de la
Santé à travers la renégociation du contrat du droit commun triennal liant l’UFM à la
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


direction d’approvisionnement dudit ministère, la recherche d’autres conventions avec
les différents organismes publics et privés tels que l’inspection de la Santé Militaire
(ISM) et les CHU, ainsi que le renouvellement des différentes certifications et
accréditations de l’UFM.

III.5.9. Etablissement Central de Gestion et de Stockage des Matériels

Au titre de l’année 2023 et du premier semestre de l’année 2024, les principales
opérations réalisées par l’Etablissement Central de Gestion et de Stockage des
Matériels (ECGSM) ont porté sur la vente des huiles usagées pour l’élimination des
risques liés au stockage des ensembles, sous-ensembles et des déchets métalliques
non sensibles réformés, des batteries réformées, du matériel de transmission, des
véhicules militaires réformés, de matériels ferrugineux réformés ainsi que des
pneumatiques réformés. L’ECGSM a procédé également à l’achat de vêtements
spéciaux, de blouses et de matériel de protection, ainsi que la réalisation des études
techniques et suivi des travaux de construction et réhabilitation des bâtiments sis à
Nouaceur.

Le programme d’action de l’ECGSM au titre de l’année 2025 prévoit notamment la
poursuite des opérations de vente du matériel réformé de la Marine Royale, des
déchets métalliques non sensibles, ainsi que l’acquisition des équipements de
protection individuelle et des matériels informatiques et bureautiques.

III.6. Domaine de l’équipement, du transport et autres infrastructures
       économiques
111.6.1. Centre National d’Études et de Recherches Routières

Les principales actions réalisées par le Centre National d’Études et de Recherches
Routières (CNERR) au titre de l’année 2023 et du premier semestre de l’année 2024,
se résument dans le tableau suivant :
                         Actions                     |   réalisations 2023   |   prévisions 2024
 Auscultation du réseau routier et évaluation de son
                                                            17.400 km              32.700 km
 état structurel et de la surface de la chaussée
  Réalisation du Rebornage du réseau routier                     --                24.000 km

En plus de ces actions, d’autres activités ont été également réalisées par le CNERR au
cours de la même période. Il s’agit principalement des actions suivantes :

► L’assistance technique à la commission nationale de qualification et de classification
  des laboratoires de bâtiments et de travaux publics ;
► Le développement de la recherche technique et de l'innovation notamment dans les
  domaines du Génie Civil et de la Recherche Routière à travers la passation de
  conventions avec des universités et/ou écoles d’ingénieurs pour des travaux de
  recherche routière ;
► L’élaboration du recueil annuel du trafic routier pour l’année 2022
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► La maintenance et l’exploitation du Système d’information Routière, ainsi que du
  système de gestion des incidents sur le réseau routier, et du relevé visuel ;
► Le traitement et l’exploitation des données des formulaires des accidents corporels
  de la circulation routière pour l’année 2022.
Par ailleurs, le Centre prévoit au titre de l’année 2025 la réalisation d’un ensemble
d’actions, dont notamment :

   La poursuite des travaux d’auscultation du réseau routier et d’évaluation de l’état
   structurel et de la surface de la chaussée, à l’aide des appareils d’auscultation ;
► La modernisation du système d’auscultation routière à travers l’achat de nouveaux
  équipements ;
   La poursuite du développement du système d’information géographique en
   procédant à la maintenance et à l’exploitation du Système d’information Routière
   (SIR), du Système de Gestion du Relevé Visuel (SGRV) et du système
   « INFOROUTE » ;
► La refonte du SIR en développant les fonctionnalités métiers routières autour de la
  nouvelle plateforme déployée ;
► L’exploitation des mesures de comptage routier pour l’élaboration du recueil annuel
  et des recueils régionaux du trafic routier.

Il1.6.2. Services de Logistique et de Matériel et Service Réseau des Services de
         Logistique et de Matériel

Les principales réalisations de ces SEGMA qui relèvent du Ministère de l’équipement
et de l’eau, au titre de l’année 2023 et du premier semestre de l’année 2024, ont
porté sur les actions suivantes :

► Le raccourcissement de la durée des dysfonctionnements du matériel des travaux
  publics (le taux de disponibilité du matériel a atteint 85%) ;
► L’amélioration de la qualité des équipements et la rénovation du parc de matériel des
  travaux publics à travers l’acquisition du matériel des travaux publics afin d’assurer
  la viabilité routière ;
   L’amélioration de la qualité du service rendu par les ponts de secours installés pour
   garantir la sécurité des usagers.
Le programme d’action pour l’exercice 2025 portera essentiellement sur le
renforcement de la disponibilité du matériel des travaux publics dans l’objectif
d’atteindre un taux de 90%, la poursuite du renouvellement du parc du matériel des
travaux publics à travers l’acquisition de nouveaux engins, ainsi que l’amélioration du
service fourni par les ponts de secours installés pour garantir la sécurité des usagers.
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


Il1.6.3. Service de Gestion des Chantiers

Les principales réalisations du Service de Gestion des Chantiers (SGC) au titre de
l’année 2023 et du premier semestre de l’année 2024 ont concerné les actions
suivantes :

► La location du matériel et des engins au profit de l’Agence du Bassin Hydraulique du
  Loukkos et de l’agence de la Moulouya pour la réalisation des opérations de
  protection contre les inondations ;
   La location du matériel et des engins au profit de l’Agence du Bassin Hydraulique du
   Bouregreg et de la Chaouia pour la réalisation des opérations de préservation des
   réserves publiques en eau ;
► La conclusion des conventions pour la location du matériel des travaux publics avec
  les Directions Provinciales de l’Equipement concernées pour le dégagement des
  éboulis du réseau routier, ainsi que le déblaiement des bâtiments administratifs et
  des logements effondrés par le séisme d’AI Haouz.
Les prévisions du SGC au titre de l’année 2025 portent essentiellement sur la location
du matériel des travaux publics pour le compte de la Direction des Aménagements
Hydrauliques, dans le but d’aménager les cours d’eau et de mettre en oeuvre le
programme de protection contre les inondations, et aussi pour le compte des Agences
de Bassins Hydrauliques en vue de les accompagner dans le programme de
préservation du patrimoine hydraulique. Également, ce SEGMA prévoit l’extension du
champ de sa clientèle pour intégrer les communes territoriales, et l’amélioration du
rendement des ateliers du parc matériel.

Il 1.6.4. Direction de la Marine Marchande

Les principales actions réalisées par la Direction de la Marine Marchande (DMM) au
titre de l’année 2023 et durant le premier semestre de l’année 2024 se résument comme
suit :
► L’élaboration d'une étude pour définir un nouveau modèle de développement du
  transport maritime des passagers sur les lignes maritimes Tanger Med - Algésiras et
  Tanger Ville - Tarifa, avec la préparation d'un plan d'investissement visant à attirer un
  acteur économique marocain capable d'exploiter ces lignes maritimes de manière
  efficace ;
   L’achèvement du processus du versement des indemnités partielles du prix du billet
   de voyage maritime en faveur des MRE dans le cadre de l'opération « Marhaba 2021 »,
   pour ceux qui n'ont pas pu finaliser leurs démarches relatives à la compensation
   lancée en 2021 ;
► La préparation d'un projet de loi relatif au transport maritime des passagers et de
  leurs bagages, stipulant les conditions et modalités de conclusion du contrat de
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


   transport, les droits et obligations des passagers, ainsi que le régime de
   responsabilité et d'indemnisation lié au transport des passagers et de leurs bagages ;
   La mise en oeuvre du plan d'action de la DMM en coordination avec l'équipe nationale
   composée de représentants des secteurs de la Marine Royale, de la pêche maritime,
   de la Direction des Ports et du Domaine Public Maritime, du secteur de la santé et de
   l'environnement, ainsi que de l'Agence Nationale des Ports ;
   La mise en place d’un système intégré pour le suivi et la surveillance des navires se
   dirigeant vers les ports marocains ou traversant les eaux territoriales marocaines, qui
   sera alimenté par différentes sources d'informations internes, notamment le réseau
   du Système d'identification Automatique (AIS).
Pour ce qui est du plan prévisionnel de la DMM au titre de l’année 2025, il s’articule en
particulier autour des actions suivantes :
► La poursuite de l'étude stratégique sur la création d'une flotte maritime commerciale
  nationale forte et compétitive dont l’objectif sera de mettre en oeuvre la quatrième
  mission de l'étude, qui consiste à accompagner le Ministère du Transport et de la
  Logistique dans l'application du plan d'action de la stratégie choisie et approuvée ;
► L’amélioration du système d'information de la Direction de la Marine Marchande
  relatif à la gestion des accostages des navires commerciaux et des gens de mer ;
► La digitalisation des services rendus aux utilisateurs ;
   La mise en place d'une stratégie nationale pour la mise en oeuvre des lignes
   directrices de 2023 sur la pollution biologique au Maroc.

Il 1.6.5. Direction Générale de la Météorologie

Les réalisations de la Direction Générale de la Météorologie (DGM) pour l’année 2023
et le premier semestre de l’année 2024, se sont articulées autour de l’extension du
réseau météorologique dans le cadre du Fonds de Lutte contre les effets des
Catastrophes Naturelles, ainsi que le développement du système de traitement des
données météorologiques, et ce, conformément aux axes ci-dessous :

► Fourniture, installation et mise en service de deux radars météorologiques Doppler
  de bande C pour la couverture de la région de Casablanca-Settat et de la région de
  Fès-Meknès ;
   Acquisition, installation et mise en service de deux radars pour la couverture des
   régions Sud Est et Sud « provinces d’Arfoud et de Tan-Tan » financés à hauteur de
   50% dans le cadre du Fonds de Lutte contre les Catastrophes Naturelles ;
   Réalisation des opérations de maintenance retenues dans les marchés-cadres du
   matériel météorologique et des équipements de pointe de la Direction Générale de
   la Météorologie, notamment, le calculateur de prévision numérique, le système du
   réseau radars météorologiques et les stations automatiques de la navigation
   aérienne ;
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


► Fourniture, installation et mise en service d'un système urbain de mesure des
  précipitations à Casablanca, Rabat et Tanger ;
► Accompagnement et assistance à la transformation statutaire de la DGM en
  établissement public doté de la personnalité morale et de l'autonomie financière ;
► Fourniture, installation et mise en service d'un système urbain de surveillance
  météorologique pour les villes de Marrakech, Fès, Agadir et Oujda ;
► Fourniture, installation et mise en service de deux systèmes d’automatisation de
  l’observation météorologique au siège de la Wilaya de l’Oriental et au Centre
  Provincial de la Météorologie d’EI Hajeb.
Par ailleurs, la DGM prévoit, au titre de l’année 2025, la réalisation des actions
suivantes :
► Renforcer l’anticipation des risques météorologiques par la mise en place d’alertes
    précoces et inclusives ;
► Fournir des services innovants et adaptés pour mieux répondre aux besoins de la
  société en intégrant les progrès scientifiques et techniques et l’intelligence
  artificielle ;
► Améliorer les observations et l’information en intégrant les nouvelles technologies au
  niveau de l’infrastructure météorologique ;
► Transformer le système de gouvernance et renforcer le partenariat et la coopération
  afin d’assurer l’efficacité des politiques, des décisions et des activités de mise en
  oeuvre.

Il 1.6.6. Direction Générale de I’Aviation Civile

Les réalisations majeures de la Direction Générale de l’Aviation Civile (DGAC) au titre
de l’année 2023 et du premier semestre de 2024 se résument comme suit :
   Le renouvellement de toutes les conventions au titre de l’année 2023 pour une durée
   d’une année et avec les mêmes conditions ;
   L’élaboration d’un accord type conforme à l’esprit de la décision de Yamoussoukro
   (DY), pour l’harmonisation des accords conclus avec les Etats africains ;
   La vérification des déclarations des émissions des compagnies RAM et AIR ARABIA
   MAROC et de l’organisme de vérification, au titre de l’année 2022, et soumission des
   déclarations à l’Organisation de l'Aviation Civile Internationale (OACI) via le registre
   central de CORSIA (CCR) ;
► La mise en oeuvre du programme de certification des aéroports ;
► La préparation des termes de référence pour l’étude relative à l’élaboration du
  schéma directeur aéroportuaire national ;
► La réalisation du programme annuel d’inspection des organismes de maintenance et
  des systèmes d’entretien des exploitants aériens ;
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


► La réalisation de 18 actions de formation du contrat de formation des cadres de la
  DGAC dans le domaine de l’aviation civile et du transport aérien (DGAC/ACAO) ;
► L’automatisation du processus de délivrance des autorisations de droits du trafic ;
► Le renforcement des missions d’observation et de veille dans le transport aérien.
Au titre de l’exercice 2025, la DGAC prévoit principalement la réalisation des actions
suivantes :
► Le suivi des conventions de partenariat conclues avec la RAM dans le cadre de la
  promotion du transport aérien domestique ;
► La mise en oeuvre du système MRV du CORSIA « Surveillance, déclaration et
  vérification » des émissions annuelles de CO2 de la RAM et MAC : validation des
  déclarations des compagnies ;
► Le renfoncement des équipes qualifiées pour réaliser les plannings annuels d’audit
  (examens de navigabilité, maintenance, gestion de navigabilité...) ;
► La réalisation du planning annuel des inspections de sécurité des aéroports ;
► La réalisation du programme annuel d’homologation des organismes de formation et
  des simulateurs de vol.

III.7. Domaine des autres actions économiques

Il 1.7.1. SEGMA chargé de la Privatisation

Au titre de l’année 2023 et du premier semestre de l’année 2024, le SEGMA chargé
de la Privatisation n’a réalisé aucune opération d’ouverture de capital ou de cession.
Pour l’année 2025, ledit SEGMA prévoit la réalisation des études préparatoires et des
missions d’évaluation et de placement portant sur le programme de cession d’une part
(ou de la totalité) du capital de certaines entreprises publiques, et ce, conformément
aux dispositions de la loi n°39-89 autorisant le transfert d’entreprises publiques au
secteur privé.

111.8. Domaine de l’agriculture et de la pêche maritime

Il1.8.1. Division de la Durabilité et d’Aménagement des Ressources Maritimes

Les actions menées par la Division de la Durabilité et d’Aménagement des
Ressources Maritimes (DDARM) au titre de l’année 2023 ont porté principalement
sur :
► La mise en oeuvre de la convention d’assurance relative à la couverture des accidents
  de travail des fonctionnaires chargés de l’observation à bord des navires de pêche ;
► L’achat de fournitures (bureau et informatiques), et l’entretien des bâtiments et du
  matériel ;
   PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


► L’actualisation et la mise à jour des informations concernant le secteur halieutique à
  travers des abonnements à des revues spécialisées ;
► L’organisation de manifestations afférentes aux opérations de contrôle ;
► La gestion du contentieux pour la protection des intérêts de la DDARM ;
► L’amélioration des conditions du contrôle ;
► La mise à niveau des services de la DDARM (locaux, équipements)
► L’équipement des services déconcentrés chargés du contrôle ;
► L’entretien et la réparation des appareils de radiocommunication en vue d’assurer la
  sécurité et le sauvetage maritime ;
► La coopération pour la promotion de la conservation et la gestion des ressources
  halieutiques.
Au titre du premier semestre de l’année 2024, la DDARM a poursuivi la réalisation de
ses activités courantes avec notamment la reconduction de la convention d’assurance
des accidents de travail du personnel chargé de l’observation à bord des navires, la
gestion du contentieux pour la protection des intérêts de la DDARM et l’amélioration
des conditions de contrôle et les autres missions, dont la finalisation est prévue d’ici la
fin de l’année.

S’inscrivant dans une démarche d’amélioration continue de la qualité de ses services
en matière de conservation et de gestion des ressources halieutiques, le plan d’action
prévu au titre de l’année 2025 est articulé autour des actions suivantes :
► La mise à niveau des services de la DDARM, notamment à travers l’aménagement
  des locaux et l’acquisition du matériel informatique et audiovisuel ;
► L’amélioration des conditions de sécurité, de contrôle et de sauvetage maritime ;
► La mobilisation des moyens financiers pour l’acquisition des équipements de contrôle
  des services déconcentrés ;
► La cotisation à des organismes internationaux, ayant leur siège au Maroc ou à
  l'étranger, chargés de la protection de la ressource halieutique.

III.8.2. Laboratoire National des Etudes et de Surveillance de la Pollution

Le tableau ci-dessous synthétise les principales actions exécutées par le Laboratoire
National des Etudes et de Surveillance de la Pollution (LNESP) au titre de l’exercice
2023 :
                                                                                             Taux de
   Objectif      Mesures prises             Indicateur de suivi   Prévisions Réalisations
                                                                                            réalisation
                 Surveillance    de ✓ Nombre des plages              196         196          100%
 Surveillance de la qualité     des ✓ Nombre des stations           497          497          100%
    l’état de    eaux            de ✓ Nombre d’échantillons/an      5100         5119         100%
l’environnement baignade            ✓ Nombre d’analyses            35700        35833         100%
                 Surveillance   de ✓ Nombre de plages               63           63          100%
                 la qualité     du ✓ Nombre des stations            126          126         100%
                                     RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


                                                                                                         Taux de
   Objectif      Mesures prises              Indicateur de suivi              Prévisions Réalisations
                                                                                                        réalisation
                sable                ✓ Nombre de catégories de déchets          3024        3024         100%
                                       marins
                                     ✓ Nombre d’échantillons                    252          252         100%
                                       (mycologiques)
                                     ✓ Nombre d’analyses (mycologiques)         1008        1008         100%
                Surveillance de la   ✓ Nombre des stations                        15         15          100%
                pollution            ✓ Nombre de campagnes                        4           3           75%
                véhiculée vers la    ✓ Nombre d’échantillons                     80          66           82%
                Méditerranée         ✓ Nombre d’analyses                        1688        1188          70%
                                     ✓ Nombre des stations                        24         24          100%
                Programmes de        ✓ Nombre de campagnes                        4           3           75%
                surveillance IMAP    ✓ Nombre d’échantillons                     112         76           68%
                                     ✓ Nombre d’analyses                        1400        1100          79%
                Surveillance de      ✓ Nombre des stations                         34         28          82%
                la        pollution  ✓ Nombre de campagnes                         4           1          25%
                véhiculée      vers  ✓ Nombre d’échantillons                      136         75          55%
                l’atlantique         ✓ Nombre d’analyses                         2720        628          23%
                Surveillance de
                                     ✓ Nombre    de jours de mesure             19710       16780          85%
                la qualité de l’air
                Validation      des
                méthodes             ✓ Nombre    d’analyses (Métaux lourds)      100         100          100%
                d’analyse
                                     ✓ Nombre    d’échantillons (physico­
                                       chimie)                                   29           29          100%
                                     ✓ Nombre    d’analyses (physico­
                Participation aux      chimie)                                   40           40          100%
                essais        inter­ ✓ Nombre    d’échantillons (métaux
                laboratoires           lourds)                                    7           7           100%
                                     ✓ Nombre    d’analyses (métaux lourds)      42          42           100%
                                     ✓ Nombre    d’échantillons (Organique)      26          26           100%
                                     ✓ Nombre    d’analyses (Organique)          186         186          100%
    Requêtes                         ✓ Nombre    d’opérations                                 2
                                                                                A la                        -
pour répondre Rejets liquides        ✓ Nombre    d’échantillons                               12
                                                                              demande
  aux plaintes                       ✓ Nombre    d’analyses                                  132
en effectuant
 des missions
                                                                                A la                        -
 in-situ et des Qualité de l’air     ✓ Nombre    de mesures                                  360
                                                                              demande
   analyses au
   laboratoire
                                     ✓ Nombre    des missions                                 1
                                                                                A la                        -
                Rejets liquides      ✓ Nombre    d’échantillons                               6
Prestations de                                                                demande
                                     ✓ Nombre    d’analyses                                  140
     services
                Emissions
                                     ✓ Nombre    de mesures                      500         192           38%
                atmosphériques
                Formation         et
                encadrement          ✓ Nombre    des stagiaires                                15
Promotion de des         stagiaires ✓ Nombre     d’échantillons                 A la          100           -
  la recherche
                dans différents ✓ Nombre         d’analyses                   demande        1500
   scientifique
                domaines         de
                l’environnement

Concernant le premier semestre de l’année 2024, les actions réalisées sont articulées
autour des activités ordinaires du laboratoire, notamment la surveillance de l’état de
l’environnement, l’appui technique des pouvoirs publics pour la résolution des conflits
environnementaux liés à la pollution, l’offre des services pour la caractérisation des
émissions gazeuses et des rejets liquides, la promotion de la recherche scientifique
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |


ainsi que l’accréditation du laboratoire en participant aux essais inter-laboratoires à
l’échelle internationale.
Le plan d’action du Laboratoire National des Etudes et de Surveillance de la Pollution
au titre de l’année 2025 envisage, essentiellement, la poursuite des actions déjà
entamées au cours des années précédentes en ce qui concerne la surveillance de la
qualité des eaux, du sable et de l'air et à répondre au mieux aux différentes requêtes
formulées tant par le secteur public que privé. Aussi, le LNESP envisage de participer
aux essais inter-laboratoires ainsi que de développer la recherche scientifique en
assurant la formation et l’encadrement des stagiaires en matière d’environnement.
                       ANNEXES




ANNEXE 1 : Attributions des SEGMA
ANNEXE 2 : Tableau récapitulatif de Pexécution des budgets
           des SEGMA au titre des années 2022 et 2023
ANNEXE 3 : Evolution des recettes des SEGMA en 2022 et
           2023
ANNEXE 4 : Evolution des dépenses des SEGMA en 2022
           et 2023
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |




ANNEXE 1 : ATTRIBUTIONS DES SEGMA
1.1. SEGMA relevant du domaine de la santé

Les SEGMA relevant du domaine de la santé concourent activement à la réalisation des
objectifs du Gouvernement en matière d’élargissement de l’accès à des soins de
qualité pour l’ensemble des citoyens et de renforcement des mesures sanitaires
préventives contre les épidémies. Les attributions de ces services ainsi que leurs
réalisations financières durant la période 2018-2023 sont présentées ci-après :

                                                      Attributions des SEGMA
                        • Soutenir les Forces Armées Royales en assurant des prestations de
                          prévention, de diagnostic, de soins, d’hospitalisation et d’expertise au profit de
 ADMINISTRATION
                          l’ensemble du personnel militaire, de leurs ayants droit, ainsi que des civils ;
  DE LA DEFENSE
                        • Concourir à la formation pratique des médecins et des étudiants en médecine et
   NATIONALE :
                          en pharmacie, ainsi qu’au développement des activités de recherche et
    Hôpitaux et
                          d’économie de santé en concert avec les facultés de médecine et les instituts de
  Centres médico-
                          formation aux carrières de santé des infirmiers ;
    chirurgicaux
                        • Contribuer aux missions humanitaires aussi bien à l’intérieur du Royaume qu’à
     militaires
                          l’étranger afin de prendre en charge, de secourir et de dispenser des soins
                          spécialisés urgents aux militaires ainsi qu’à la population civile.
                        • Dispenser, avec ou sans hébergement, des prestations de diagnostic, de soins et
                          de services aux malades, blessés et parturientes ;
                        • Garantir la permanence des soins et assurer des prestations de soins et d’aide
 MINISTERE DE LA          médicale en urgence ;
 SANTE ET DE LA         • Contribuer aux actions de médecine préventive, d’éducation pour la santé, d’aide
   PROTECTION             médicale urgente en partenariat avec les acteurs concernés ;
    SOCIALE :           • Assurer la formation pratique des étudiants en médecine et en pharmacie et des
    Hôpitaux et           élèves des instituts et des écoles de formation professionnelle et de formation des
  Centres d’appui         cadres, en rapport avec le domaine de la santé, ainsi que la formation continue des
                          professionnels et des gestionnaires de santé ;
                        • Participer à la réalisation des activités de recherche en matière de santé publique,
                          d’économie de la santé et d’administration sanitaire.
                        • Promouvoir le don du sang au niveau national ;
 MINISTERE DE LA
 SANTE ET DE LA         • Améliorer, mettre au point et diffuser les techniques transfusionnelles ;
   PROTECTION           • Adapter les activités aux évolutions médicales et techniques ;
     SOCIALE :          • Fabriquer et distribuer gratuitement des réactifs des produits sanguins ;
 Centre National de     • Imposer un contrôle qualité et assurer un audit annuel à tous les CTS (Centres de
    Transfusion           Transfusion Sanguine) ;
    Sanguine et         • Fournir l’équipement et les moyens de fonctionnement des différents CTS ;
  d’Hématologie
                        • Construire et aménager les CTS.
 MINISTERE DE LA        • Promouvoir le don du sang au niveau de Casablanca et de sa Région ;
 SANTE ET DE LA         • Organiser des collectes du sang à l’extérieur et à l’intérieur ;
   PROTECTION           • Réaliser les examens obligatoires sur le sang ;
    SOCIALE :
                        • Assurer l’approvisionnement régulier en poches des Produits Sanguins Labiles
 Centre Régional de
    Transfusion           (PSL) de l’ensemble des établissements publics ou privés de Casablanca et de sa
Sanguine-Casablanca       Région.
 MINISTERE DE LA        • Développer l’expertise, l’appui scientifique et technique et la conduite des
 SANTE ET DE LA           recherches dans le domaine de la biologie sanitaire ;
   PROTECTION           • Proposer des normes en matière de biologie sanitaire et développer des systèmes
                              RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME

    SOCIALE :         de vigilance relatifs à la santé humaine ;
 Institut National   • Participer à la formation du personnel médical, paramédical et scientifique et
    d’Hygiène          diffuser l’information en rapport avec ses compétences ;
                     • Promouvoir la coopération nationale et internationale en matière de biologie et de
                       vigilance.
                     • Veiller à la mise en application de la réglementation en matière de protection
                       contre les rayonnements ionisants ;
                     • Codifier les mesures applicables dans tout établissement utilisant les rayonnements
                       ionisants et veiller à leur mise en application ;
MINISTERE DE LA
                     • Procéder au contrôle préalable et a posteriori de toute installation technique
SANTE ET DE LA
                       utilisant les rayonnements ionisants à des fins médicales ou non médicales ;
  PROTECTION
   SOCIALE :         • Contrôler les importations, les utilisations, le transport et le stockage des sources
                       des rayonnements ionisants et de la radiologie aux frontières ;
Centre National de
 Radio-protection    • Surveiller la radioactivité dans l’environnement, les denrées alimentaires et les eaux
                       potables ;
                     • Participer à l’élaboration des normes en matière de radioprotection et de sûreté
                       nucléaire, et à la réalisation des études afférentes à l’installation ou au
                       démantèlement des sources de radiations ionisantes et à la radioprotection.
                     • Arrêter les normes de fabrication, de conditionnement, de circulation, de vente et
MINISTERE DE LA        de   stockage    des    médicaments,     des    produits   pharmaceutiques      et
SANTE ET DE LA         parapharmaceutiques ;
  PROTECTION         • Fixer le cadre des prix des médicaments et des spécialités pharmaceutiques ;
    SOCIALE :        • Assurer le contrôle technique et de qualité dans le cadre de la législation et de la
   Direction du        réglementation en vigueur ;
Médicament et de
                     • Effectuer l’inspection des officines, grossisteries et laboratoires de fabrication ;
  la Pharmacie
                     • Délivrer les visas et autorisations de débit des produits pharmaceutiques.
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |




   Evolution du nombre des SEGMA relevant du
                                                   Evolution du taux de recouvrement des
               domaine de la santé
                                                dépenses par les recettes propres des SEGMA
                                                      relevant du domaine de la santé
                                                                                          90%
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


1.2. SEGMA relevant du domaine de l’enseignement, de la formation
      professionnelle et de la formation des cadres

La formation dispensée par ces SEGMA consiste à doter les secteurs concernés de
ressources humaines qualifiées qui pourront les accompagner dans leur processus
de développement. Il s’agit, notamment, des domaines du tourisme, de l’artisanat,
de l’agriculture, de la pêche maritime, des mines, de l’aménagement et de
l’urbanisme, du sport, de la géologie, des statistiques, de l’informatique, de
l’économie appliquée, de l’administration publique et de la santé. Les attributions de
ces services ainsi que leurs réalisations financières durant la période 2018-2023 sont
présentées ci-après :
    Libellé des SEGMA                                  Attributions des SEGMA
   HAUT COMMISSARIAT
          AU PLAN :           • Dispenser la formation initiale et la formation continue dans les domaines de
     Institut National de       la statistique, de l’économie appliquée, de l’informatique, de la démographie,
        Statistique et          de l’actuariat finance et de l’aide à la décision.
   d’Économie Appliquée
   HAUT COMMISSARIAT
                              • Dispenser la formation initiale destinée aux informatistes et aux
          AU PLAN :
                                informatistes spécialisés, la formation continue notamment en matière des
   École des Sciences de
                                NTIC ainsi que les actions de recherche et de développement.
        l’information
                              • Dispenser la formation initiale au profit des techniciens, des techniciens
                                spécialisés et des ouvriers qualifiés en agriculture, dans différentes
                                spécialités en production végétale et animale ;
        MINISTERE DE          • Assister et former les jeunes promoteurs sur des projets dans les domaines
  L'AGRICULTURE, DE LA          agricoles ;
   PECHE MARITIME, DU         • Assurer la formation continue des ouvriers des exploitations agricoles ;
      DEVELOPPEMENT           • Former et assister des maîtres de stage ;
    RURAL ET DES EAUX         • Dispenser la formation par apprentissage aux jeunes déscolarisés issus du
          ET FORETS :           milieu rural ;
    Instituts et centres de   • Suivre l’insertion des lauréats ;
  formation œuvrant dans      • Réaliser des études et des enquêtes pour l’évaluation des besoins en
     le domaine agricole        compétences du secteur, et ce en vue d’élaborer un répertoire de métiers et
                                d’emplois ;
                              • Présenter des conseils aux professionnels dans les domaines techniques et
                                socio-professionnels.
       MINISTERE DE
  L'AGRICULTURE, DE LA
   PECHE MARITIME, DU         • Former les ingénieurs des Eaux et Forêts ;
     DEVELOPPEMENT            • Animer des sessions de formation continue ;
   RURAL ET DES EAUX          • Effectuer toutes études et recherches ayant trait à la foresterie et à la
        ET FORETS :             gestion durable des ressources naturelles et environnementales.
      École Nationale
   Forestière d’ingénieurs
       MINISTERE DE            Former les ressources humaines nécessaires à la conduite, à l’exploitation et
  L'AGRICULTURE, DE LA         à la maintenance de la flotte de pêche et des unités d’industrie de pêche.
   PECHE MARITIME, DU          Ces instituts et centres oeuvrent particulièrement pour :
     DEVELOPPEMENT            • Améliorer qualitativement la formation professionnelle en pêche maritime
  RURAL ET DES EAUX ET          (résidentielle, alternée et par apprentissage) ;
          FORETS :            • Organiser des       cycles    de   formation   continue,   d’alphabétisation
   Instituts et centres de      fonctionnelle, de vulgarisation, de perfectionnement et de recyclage, en vue
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



 Libellé des SEGMA                                     Attributions des SEGMA
formation opérant dans         de contribuer à la promotion professionnelle des marins en activité ;
le domaine de la pêche       • Valoriser les acquis professionnels par la mise en œuvre d’actions de
       maritime                formation continue ;
                             • Accompagner le programme de mise à niveau et de modernisation de la
                               flotte de pêche côtière et artisanale à travers des actions d’alphabétisation
                               professionnelle, de vulgarisation et d’encadrement.
                             • Former des artisans innovateurs et qualifiés capables d’assurer la
                               préservation du patrimoine culturel existant et de créer de nouveaux
     MINISTERE DU              produits de qualité ;
     TOURISME, DE            • Organiser des actions de formation continue, de perfectionnement des
  L’ARTISANAT ET DE            artisans et des chefs d’entreprises d’artisanat, ainsi que des séminaires, des
L’ECONOMIE SOCIALE             conférences, des journées d’études, des stages et des ateliers pratiques ;
     ET SOLIDAIRE :          • Assurer des prestations rémunérées, réalisées par les établissements de
SEGMA opérant dans le          formation, sous forme de travaux à façon aux tiers ;
 domaine de l’artisanat      • Réaliser des recettes à travers la vente d’articles d’artisanat et chefs-
                               d’œuvre réalisés par les stagiaires et les apprentis, dans le cadre des travaux
                               pratiques.
                             • Concevoir et mettre en œuvre les programmes et les actions de formation
                               transverse au profit du personnel du Ministère de l’Economie et des
                               Finances ;
     MINISTERE DE            • Accompagner les actions de formation spécifiques des Directions de ce
 L’ECONOMIE ET DES             département ;
      FINANCES :             • Concevoir et mettre en œuvre les programmes et les actions de formation
Division Administrative        en appui aux réformes mises en œuvre par le département ;
                             • Mettre en œuvre les programmes d’insertion au profit des nouvelles recrues
                               de ce département ;
                             • Promouvoir des actions de partenariat aux niveaux national et international.
                             • Assurer la formation continue et les cycles de perfectionnement au profit
                               du personnel du Ministère et des tiers ;
                             • Organiser les manifestations se rapportant au domaine d’activités du
                               Ministère pour le compte des tiers ;
      MINISTERE              • Offrir des prestations permettant aux stagiaires externes de parfaire leurs
  DE L’EDUCATION               connaissances et de mettre en pratique leurs compétences techniques et
   NATIONALE, DU               professionnelles ;
PRESCOLAIRE ET DES           • Mettre en œuvre des actions de conseil, d’assistance et d’accompagnement
       SPORTS :                des administrations publiques, des établissements publics et des
Division des Stratégies        collectivités territoriales et autres entités dans les domaines liés à
     de Formation              l’enseignement et à l’éducation ;
                             • Assurer l’hébergement et la restauration au profit des tiers pour toute
                               manifestation éducative, scientifique, culturelle et sociale ;
                             • Publier et vendre les documents et assurer la location des locaux et du
                               matériel.
  MINISTERE DE LA            • Institut des Mines de Touissit-Oujda : Il a pour mission la formation des
     TRANSITION                techniciens en topographie et en électromécanique destinés aux secteurs
 ENERGETIQUE ET DU             minier et industriel ;
  DEVELOPPEMENT
                             • Institut des Mines de Marrakech : Il a pour mission la formation des
      DURABLE :
                               techniciens spécialisés (Bac+2) dans les métiers inhérents à la géologie
Écoles opérant dans le
                               appliquée, à l’exploitation des mines et carrières, à la chimie industrielle et
domaine de l’énergie et
                               à l’électromécanique.
      des mines
   MINISTERE DU              • Dispenser un enseignement supérieur pour la formation des cadres destinés
TRANSPORT ET DE LA             aux différentes branches de l’activité maritime ;
    LOGISTIQUE :
                             • Entreprendre des études et des recherches liées à la formation maritime ;
  Institut Supérieur
                                   RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME

|     Libellé des SEGMA       |                            Attributions des SEGMA                                   |
      d’Études Maritimes          • Assurer la formation et le perfectionnement du personnel des opérateurs
                                    du transport maritime.
         MINISTERE DE
                                  • Assurer des prestations de formation, de recyclage et de perfectionnement
     L’EQUIPEMENT ET DE
                                    des agents et des techniciens des administrations. Les domaines de
             L’EAU :
                                    formation concernent particulièrement la conduite, l’entretien et la
     Institut de Formation
                                    maintenance des engins des travaux publics ainsi que la maintenance,
         aux Engins et à            l’entretien et l’extension du réseau routier.
       l’Entretien Routier
        MINISTERE DE              • Assurer et supporter les frais quotidiens de fonctionnement du Centre
     L’EQUIPEMENT ET DE             d’Accueil et de Conférences (CAC) ;
            L’EAU :
                                  • Assurer la sauvegarde et la maintenance du patrimoine du CAC ainsi que
    Service de la Formation
                                    son développement.
           Continue
        MINISTERE DE
     L'AMENAGEMENT DU
    TERRITOIRE NATIONAL,
     DE L'URBANISME, DE  • Former des architectes ;
     L'HABITAT ET DE LA  • Contribuer à la recherche et à la diffusion des connaissances dans les
       POLITIQUE DE LA     domaines liés à l’architecture.
            VILLE :
       Écoles Nationales
        d’Architecture
                                  • Former des cadres supérieurs spécialisés dans les techniques de
                                    l’aménagement et de l’urbanisme destinés à servir dans les organismes
                                    publics et privés ;
          MINISTERE DE            • Concevoir et réaliser des cycles de formation continue au profit du
     L'AMENAGEMENT DU               personnel du ministère de tutelle et de ses services extérieurs, au profit
    TERRITOIRE NATIONAL,            d’autres départements ministériels ainsi qu’au profit d’organismes publics
     DE L'URBANISME, DE             et privés ;
     L'HABITAT ET DE LA
                                  • Réaliser, pour le compte des administrations de l’État, des établissements
       POLITIQUE DE LA
                                    publics, des collectivités territoriales et des organismes privés, des études
              VILLE :
                                    dans le domaine de l’aménagement et de l’urbanisme ;
         Institut National
       d’Aménagement et           • Contribuer au développement de la recherche en matière d’organisation de
           d’Urbanisme              l’espace et à la diffusion des connaissances ;
                                  • Organiser des manifestations et des activités scientifiques relatives à la
                                    gestion des villes, à l’aménagement du territoire, à l’habitat et au
                                    développement durable.
                                  • Assurer la formation, le recyclage et le perfectionnement des cadres
                                    relevant du Ministère de l’intérieur ;
                                  • Assurer l’information et la formation des élus en matière d’administration
                                    et d’ingénierie de la formation, notamment à travers l’identification des
                                    besoins de formation, le montage des programmes de formation, le suivi,
                                    l’évaluation et l’audit ;
        MINISTERE DE
                                  • Mettre à disposition des locaux, les infrastructures, les ateliers et les
        L’INTERIEUR :
                                    matériels pédagogiques ;
         Direction du
                                  • Assurer la formation, notamment d’intégration, initiale, continue,
      Développement des
                                    académique ou de préparation aux concours et aux examens d’aptitudes
     Compétences et de la
                                    professionnelles ;
    Transformation Digitale
                                  • Assurer le transport, l’hébergement et la restauration des bénéficiaires de
                                    la formation ;
                                  • Réaliser toute autre prestation dont l’objectif est de permettre la
                                    qualification des bénéficiaires de la formation, le renforcement de leurs
                                    capacités de gestion et la mise en pratique de leurs compétences
                                    professionnelles et techniques.
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



  Libellé des SEGMA                                   Attributions des SEGMA
                               Organiser des manifestations en rapport avec les domaines d’intervention
     MINISTERE DE              du ministère de l’inclusion Economique, de la Petite Entreprise, de l’Emploi
      L’INCLUSION              et des Compétences et des établissements sous sa tutelle ;
 ECONOMIQUE, DE LA             Organiser des sessions de formation, de rencontres et de séminaires au
PETITE ENTREPRISE, DE          profit des organisations, des administrations, des établissements publics,
   L’EMPLOI ET DES             des organisations syndicales ou professionnelles, des associations et des
    COMPETENCES :              particuliers ;
Division de la Formation       Louer des locaux (salles de formation, salles de conférences et ateliers) ;
                               Louer des infrastructures et des matériels pédagogiques ;
                               Assurer la formation théorique et pratique des cadres supérieurs dans les
                               domaines des médias et de la communication des organisations ;
    MINISTERE DE LA            Organiser des cycles de perfectionnement et de formation continue en la
    JEUNESSE, DE LA            matière à travers des séminaires, des colloques et des stages de formation ;
   CULTURE ET DE LA            Contribuer au développement de la pratique professionnelle dans les
   COMMUNICATION :             domaines des médias et de la communication, et promouvoir la recherche
  Institut Supérieur de        scientifique et académique dans ces domaines ;
  l’information et de la       Réaliser des études au profit des administrations, des établissements
      Communication            publics, des collectivités territoriales et du secteur privé, ainsi que des
                               sondages d’opinion et des campagnes médiatiques dans les divers
                               domaines en collaboration avec des organismes nationaux ou étrangers.
   MINISTERE DE LA
   JEUNESSE, DE LA             Combler le vide en matière de formation dans les métiers de l’audiovisuel
  CULTURE ET DE LA             et du cinéma et accompagner l’évolution desdits métiers ;
  COMMUNICATION :              Satisfaire les demandes, de plus en plus grandes, en spécialistes dans ces
 Institut Supérieur des        domaines au moment où le Maroc est devenu un pays privilégié de tournage
Métiers de l’Audiovisuel       cinématographique de dimension internationale.
      et du Cinéma
                               Former les cadres supérieurs et effectuer de la recherche scientifique, ainsi
       MINISTERE               que l’expertise et le Consulting dans le domaine des sports ;
   DE L’EDUCATION              Assurer la gestion des centres de formation de Rabat Yaâcoub El Mansour
   NATIONALE, DU               et de Moulay Rachid des sports ;
 PRESCOLAIRE ET DES
                               Organiser des stages de préparation Olympique, des séminaires et des
        SPORTS :
                               colloques ;
    Institut Royal de
 Formation des Cadres          Animer des sessions de formation continue au profit des organismes publics
 de la Jeunesse et des         ou privés et des individus.
          Sports
                               Assurer la formation des cadres supérieurs médicaux et non médicaux
  MINISTERE DE LA              appartenant à des organismes publics et privés de santé, dans les domaines
   SANTE ET DE LA              de l’administration sanitaire et de la santé publique ;
PROTECTION SOCIALE :           Organiser des cycles de formation continue au profit des professionnels de
  Ecole Nationale de           santé ;
    Santé Publique             Participer à la réalisation des études et des recherches sur les systèmes de
                               santé et contribuer à la diffusion de la connaissance dans ces domaines.
    MINISTERE DU
    TOURISME, DE
 L’ARTISANAT ET DE             Doter le secteur du tourisme et de l'hôtellerie en profils adéquats pour
L’ECONOMIE SOCIALE             l’exercice des fonctions inhérentes à la restauration, à l’hébergement et à
    ET SOLIDAIRE :             l’accompagnement.
SEGMA opérant dans le
 domaine du tourisme
              RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME




H Dépenses   S Recettes          H Recettes propres   H Subventions   S Excédents reportés
      PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



   1.3. SEGMA relevant du domaine des activités récréatives

   Lesdits SEGMA sont chargés de la gestion des infrastructures sportives et
   culturelles. Ils assurent l’organisation des rencontres sportives nationales et
   internationales ainsi que des diverses manifestations artistiques et culturelles. Les
   attributions de ces services ainsi que leurs réalisations financières durant la période
   2018-2023 sont présentées ci-dessous :
  Libellé des SEGMA_________________________ Attributions des SEGMA
                          Organiser de       prestigieuses   manifestations   golfiques    nationales   et
                          internationales :
                            ►    Manifestations nationales :
                              • Coupe de la Fête du Trône ;
                              • Coupe de la Fête de la Jeunesse ;
                              • Coupe de la Marche Verte ;
CHEF DU GOUVERNEMENT :        • Championnat du Maroc.
  Royal Golf Dar Es Salam   ►     Manifestations internationales :
                              • Trophée HASSAN II de golf ;
                              • Challenge HASSAN II de golf ;
                              • Open du Maroc ;
                              • Classic de Dar Es Salam.
                          Outre les manifestations sportives sus-indiquées, plusieurs autres compétitions
                          se déroulent sur les parcours du Royal Golf Dar Es Salam.

      MINISTERE DE              • Offrir à l’élite nationale des équipements sportifs de haut niveau respectant les
L’EDUCATION NATIONALE,            contraintes techniques et fonctionnelles de la pratique sportive ;
 DU PRESCOLAIRE ET DES          • Participer à la promotion du sport à l’échelle régionale voire nationale ;
        SPORTS :                • Abriter des manifestations sportives permanentes et occasionnelles dans les
     Complexe sportif             meilleures conditions ;
  Mohammed V de Casa et         • Créer et encadrer techniquement les écoles de sport qui sont actuellement au
     base nautique de             nombre de 500 écoles réparties à travers le Royaume ;
       Mohammedia
                                • Organiser des manifestations artistiques, culturelles et politiques.
       MINISTERE DE
L’EDUCATION NATIONALE,          • Élargir la base des pratiquants de la natation surtout au sein des jeunes ;
 DU PRESCOLAIRE ET DES
                                • Développer l’autofinancement des activités liées à cette discipline sportive ;
          SPORTS :
                                • Accueillir les manifestations sportives (en natation) ;
  Service du Contrôle des
   Etablissements et des        • Créer et encadrer les écoles de natation.
      Salles Sportives
                                • Abriter les rencontres de jeunes, les colonies de vacances pour les enfants et
     MINISTERE DE LA              les adolescents, les séminaires, les sessions de formation et les activités
     JEUNESSE, DE LA              éducatives, culturelles et sportives ;
    CULTURE ET DE LA            • Accueillir les associations, les organismes et les institutions œuvrant dans le
    COMMUNICATION :               domaine de la jeunesse et de l’enfance, ainsi que les particuliers et les familles
 Complexe Moulay Rachid           pour des activités d’estivage et de tourisme ;
   de la Jeunesse et de         • Accueillir les concentrations des fédérations et des clubs sportifs ;
  l’Enfance de Bouznika         • Abriter les sessions de formation et les réunions pour les organismes publics
                                  et privés.
 MINISTERE DES HABOUS           • Préserver la mémoire et mettre en valeur le patrimoine hydraulique marocain,
     ET DES AFFAIRES              que ce soit dans son histoire ou sa gestion ;
        ISLAMIQUES :            • Offrir aux visiteurs la possibilité de découvrir la dimension spirituelle de l’eau,
 Musée Mohammed VI pour           ses rituels, ses usages économiques et ses techniques traditionnelles ;
  la civilisation de l’eau au   • Appréhender la structure moléculaire et le cycle de l’eau, les systèmes
             Maroc                d’irrigation au Maroc, le captage des eaux et le droit coutumier.
                           RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME




SEGMA relevant du domaine des activités          SEGMA relevant du domaine des activités
        récréatives (En MDH)                             récréatives (En MDH)
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



1.4. SEGMA relevant du domaine des autres actions sociales
Ils sont chargés de répondre à des besoins très particuliers de certaines catégories
de population partageant des caractéristiques communes. C’est le cas notamment des
personnes à besoins spécifiques, des pèlerins aux lieux saints de l’Islam, des détenus,
des victimes des accidents de travail et des membres de la communauté marocaine
résidant à l’étranger. Les attributions de ces services ainsi que leurs réalisations
financières durant la période 2018-2023 sont présentées ci-dessous :
  Libellé des SEGMA                                  Attributions des SEGMA
     MINISTERE DES
                              Assurer l’encadrement des pèlerins marocains aussi bien à l’intérieur du
    HABOUS ET DES
                              Royaume, qu’à l’extérieur par l’intermédiaire des membres de la délégation
AFFAIRES ISLAMIQUES :
                              marocaine du pèlerinage.
 Division du Pèlerinage
      DELEGATION
      GENERALE A
   L’ADMINISTRATION           S’occuper de la gestion, du contrôle et de l’exploitation rationnelle des
     PENITENTIAIRE            différentes unités de production au sein des établissements pénitentiaires ;
ET A LA REINSERTION :         Assurer la commercialisation de la production des exploitations agricoles et
  Service des Unités de       des ateliers au sein des établissements pénitentiaires.
 Formation Artistique et
        Artisanale
     MINISTERE DES
        AFFAIRES
  ETRANGERES, DE LA           Apporter une réponse convenable aux attentes de la communauté marocaine
     COOPERATION              résidant à l’étranger et des autres usagers des services consulaires, aussi bien
   AFRICAINE ET DES           à l’étranger qu’au Maroc ;
MAROCAINS RESIDANT            Veiller à la revalorisation de l’image des représentations          consulaires
     A L'ÉTRANGER :           marocaines à l’étranger et des services consulaires au Maroc.
  Direction des Affaires
 Consulaires et Sociales
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME




  Evolution du nombre des SEGMA relevant du              Evolution du taux de recouvrement des dépenses
      domaine des autres actions sociales                 par les recettes propres des SEGMA relevant du
                                                                domaine des autres actions sociales
                                                                                              143%




2018     2019      2020     2021     2022             2018        2019      2020    2021       2022       2023

  Evolution des dépenses et des recettes des               Evolution de la structure des recettes des SEGMA
   SEGMA relevant du domaine des autres                  relevant du domaine des autres actions sociales (En
          actions sociales (En MDH)                                               MDH)




  2018    2019      2020     2021    2022      2023   2018        2019      2020     2021       2022       2023

                 I Dépenses S Recettes                       l Recettes propres     S Excédents reportés
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



1.5. SEGMA relevant du domaine des pouvoirs publics et services généraux
Les prestations offertes par ces SEGMA englobent l’ensemble des opérations de l’État
au profit des activités à caractère général. Il s’agit notamment des services communs
à l’ensemble des administrations, des services chargés du maintien de l’ordre, de la
justice ainsi que des services de l’économie et des finances. Les attributions de ces
SEGMA ainsi que leurs réalisations financières durant la période 2018-2023 se
présentent comme suit :

 Libellé des SEGMA                                  Attributions des SEGMA
 ADMINISTRATION DE
      LA DEFENSE
                              Assurer l’approvisionnement des Forces Armées Royales, de la Gendarmerie
     NATIONALE :
                              Royale et des établissements publics et privés en masques chirurgicaux et de
  Unité de Fabrication
                              protection respiratoire.
   de Masques de la
  Gendarmerie Royale
                              Promouvoir et coordonner l’importation, l’exportation, le traitement, la vente
                              et l’utilisation des produits et services en relation avec les techniques de
                              détection par satellite sur le territoire national, et en assurer la conservation.
                              De façon opérationnelle, le CRTS assure les tâches suivantes :
 ADMINISTRATION DE            Recenser, centraliser et coordonner les besoins des administrations ou
     LA DEFENSE               organismes dépendant de la télédétection afin de leur présenter des
     NATIONALE :              demandes d’achats groupées et cohérentes ;
    Centre Royal de           Importer, acquérir tant au Maroc qu’à l’étranger, conserver, dupliquer, traiter,
 Télédétection Spatiale       distribuer, vendre ou proposer à l’utilisation les produits et les services de la
        (CRTS)                télédétection ;
                              Aider et assister les utilisateurs publics ou privés, sous toutes les formes utiles,
                              afin de leur permettre une utilisation efficace des produits de la télédétection ;
                              Contrôler l’usage des produits de la télédétection afin d’en sauvegarder une
                              utilisation pacifique et conforme aux intérêts du Royaume.
  ADMINISTRATION DE           Se charger de découper, délimiter et dénaturer les matériels arrivés en fin de
      LA DEFENSE              potentiel et jugés hors service. Cette opération donne lieu à un volume
      NATIONALE :             consistant de ferraille et de déchets métalliques, dont la vente permettrait aux
  Etablissement Central       FAR de réaliser des recettes, qui pourront aider à l’entretien des bâtiments et
    de gestion et de          à l’acquisition des équipements spécifiques nécessaires au fonctionnement du
 stockage des matériels       service.
                              Collecter, traiter et diffuser les documents relatifs au développement national
                              économique et social, produits au Maroc ou à l’étranger ;
                              Consolider le fonds documentaire national et faciliter l’accès des différents
                              utilisateurs à l’information sous ses diverses formes ;
 HAUT COMMISSARIAT
     AU PLAN :                Renforcer le fonds documentaire national par le recours aux sources
                              d’information étrangères, soit par connexion en ligne ou par acquisition de
  Centre National de
   Documentation              banque de données ou de documents ;
                              Développer et coordonner les activités du réseau national d’information,
                              établir des passerelles avec les réseaux sectoriels nationaux spécialisés et
                              renforcer la coordination avec le réseau et les systèmes d’information
                              internationaux et régionaux.
                              Financer les actions visant l’amélioration des conditions de travail du
     MINISTERE DE             personnel de la TGR et renforcer la sécurité de ses locaux et de ses systèmes
  L’ECONOMIE ET DES           d’information ;
      FINANCES :              Financer les actions visant l’amélioration des conditions d’accueil et la qualité
 Trésorerie Générale du
                              des prestations offertes aux clients et aux partenaires ;
       Royaume
                              Recouvrer les coûts et les rémunérations afférentes aux diverses prestations
                              RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


Libellé des SEGMA                                 Attributions des SEGMA
                           offertes par la TGR dont notamment la prise en charge des dossiers de
                           créances, le traitement de la paie, la prise en charge du règlement des pensions
                           et la gestion des bons du trésor et des comptes des clients.
   MINISTERE DE
L’ECONOMIE ET DES
                          • Recouvrer une partie des coûts générés par les prestations de formation,
    FINANCES :
                            dispensées par l’Administration des Douanes et Impôts Indirects, à ses
 Administration des
                            partenaires et à des douaniers des pays amis.
 Douanes et Impôts
      Indirects
                          • Imprimer les publications et les périodiques du ministère de la Jeunesse, de la
                            culture et de la communication ;
  MINISTERE DE LA
                          • Réaliser les travaux de tirages concernant les volets culturels,
  JEUNESSE, DE LA
                            communicationnels et administratifs ;
 CULTURE ET DE LA
                          • Imprimer les publications des intellectuels, hommes de lettres et de sciences,
 COMMUNICATION :
                            jeunes talents, traducteurs, artistes et tous les intervenants dans le domaine
  Imprimerie dar Al         de la promotion du livre ;
       Manahil
                          • Diversifier ses ressources financières pour améliorer               sa    capacité
                            d’autofinancement et la couverture des dépenses engagées.
  MINISTERE DE LA
      JUSTICE :           • Publier les ouvrages, recueils, bulletins et rapports à caractère judiciaire ;
Centre de Publication     • Reproduire les arrêts, textes de lois, études, commentaires et notes de
et de Documentation         jurisprudence sur papier, support informatique et autre ;
Judiciaire de la Cour     • Produire les photocopies des documents.
    de Cassation
                          • Confectionner et diffuser les éditions arabes et françaises du Bulletin Officiel
                            (BO) du Royaume ;
    SECRETARIAT           • Réaliser les travaux d’impression pour le compte des administrations
    GENERAL DU              publiques et procéder au tirage des projets de lois déposés au Parlement, ainsi
  GOUVERNEMENT :            qu’à la mise sous forme de brochure des principaux textes législatifs et
     Direction de           réglementaires ;
l’imprimerie Officielle   • Contribuer à l’alimentation du site Internet du Secrétariat Général du
                            Gouvernement qui contient tous les numéros des éditions du BO parus depuis
                            1912, et auxquels l’accès est gratuit.
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |




    Evolution du nombre des SEGMA relevant du        Evolution du taux de recouvrement des
      domaine des pouvoirs publics et services   dépenses par les recettes propres des SEGMA
                    généraux                      relevant du domaine des pouvoirs publics et
                               RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


1.6. SEGMA relevant du domaine de l’équipement, du transport et autres
      infrastructures économiques
Ces services fournissent des prestations visant à développer l’activité de
l’équipement, du transport et des autres infrastructures économiques. Les attributions
de ces SEGMA ainsi que leurs réalisations financières durant la période 2018-2023 se
présentent comme suit :

  Libellé des SEGMA_______________________ Attributions des SEGMA
                            • Exécuter le plan d’action de la Direction des Routes (DR) relatif à l’acquisition
                              du matériel de Travaux Publics (TP), du parc automobile et des ponts de
                              secours ;
                            • Assurer la gestion administrative du parc matériel et du parc automobile de la
      MINISTERE DE            DR ;
  L’EQUIPEMENT ET DE        • Assurer la coordination des Services de Logistique et de Matériel (SLM) en
          L’EAU :             matière de mobilisation et d’utilisation du parc matériel ;
  Service du Réseau des     • Assurer le pilotage et l’appui nécessaire aux SLM et à l’ensemble des DRET/
  Services de Logistique      DPET (Directions Régionales et Provinciales de l’Équipement et du Transport)
      et de Matériel          en matériel de gestion du parc matériel nécessaire à leur intervention ;
                            • Gérer les ponts de secours et exécuter les travaux de leur montage,
                              démontage et entretien ;
                            • Apporter l’assistance technique aux collectivités territoriales et aux différents
                              organismes publics en matière d’expertise et d’acquisition du matériel de TP.
                            • Assurer la location et la gestion du matériel de TP dont ils disposent ;
                            • Intervenir rapidement lors des travaux de déneigement, de désensablement
                              ainsi qu’en cas d’événements exceptionnels tels que les dégâts de crues ;
      MINISTERE DE          • Réaliser les travaux d’aménagement de pistes de désenclavement du monde
  L’EQUIPEMENT ET DE          rural ;
          L’EAU :           • Encadrer les parcs provinciaux et assurer l’audit des accidents mortels au
  Services de Logistique      niveau de leurs régions ;
      et de Matériel        • Gérer les ponts de secours et exécuter les travaux de leur montage,
                              démontage et entretien ;
                            • Contribuer au renouvellement du matériel en cohérence avec la stratégie de
                              la Direction des Routes.
                            • Appliquer la politique du Ministère du Transport et de la Logistique en ce qui
                              concerne la tutelle sur les établissements publics dont l’activité est en rapport
                              avec le domaine aérien ;
      MINISTERE DU          • Assurer la sécurité et la régularité de la navigation aérienne et contrôler et
  TRANSPORT ET DE LA          coordonner les activités aéronautiques ;
       LOGISTIQUE :
                            • Préparer les accords internationaux et établir les textes réglementaires
   Direction Générale de
                              concernant la navigation aérienne, le transport aérien et l’exploitation
      l’Aviation Civile
                              aérienne et veiller à leur application ;
                            • Veiller au contrôle des opérations relatives à la sécurité aéronautique et à la
                              réglementation de l’exploitation technique des aéronefs.
                            • Assurer la gestion administrative des gens de mer ;
      MINISTERE DU
                            • Assurer la gestion administrative et technique des navires et des engins
  TRANSPORT ET DE LA
                              nautiques de plaisance ;
       LOGISTIQUE :
                            • Délivrer l’autorisation pour l’exercice d’activités maritimes ;
   Direction de la Marine
        Marchande           • Assurer les services de surveillance de la navigation maritime rendus aux
                              navires touchant les ports marocains de commerce.
     MINISTERE DE           • Ausculter les chaussées ;
  L’EQUIPEMENT ET DE        • Réaliser et administrer la banque de données routières ;
PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



Libellé des SEGMA          I                             Attributions des SEGMA
       L’EAU :                 • Réaliser les études et les recherches techniques routières ;
  Centre national              • Assurer l’assistance et la formation sur les techniques routières ;
   d’Etudes et de
                               • Promouvoir la qualité dans le domaine des études et des travaux routiers.
Recherches Routières
                               • Assurer la location d’engins des travaux publics ;
    MINISTERE DE
L’EQUIPEMENT ET DE             • Effectuer de l’expertise en gestion du matériel ;
        L’EAU :                • Réparer les engins et le matériel de travaux publics ;
Service de Gestion des         • Assurer l’assistance et la formation sur les techniques de réalisation et de
       Chantiers                 maintenance des aménagements hydriques.
                               • Assurer les activités relatives      aux   informations   météorologiques     et
                                 climatologiques nécessaires ;
    MINISTERE DE               • Effectuer les études et les recherches atmosphériques de météorologie et de
L’EQUIPEMENT ET DE               climatologie théoriques, expérimentales et appliquées ainsi que les études et
        L’EAU :                  les recherches connexes en rapport avec sa mission ;
Direction Générale de          • Participer à la préparation des accords internationaux en liaison avec les
   la Météorologie               administrations intéressées concernant les domaines de sa compétence,
                                 établir les textes réglementaires relatifs à la météorologie et en assurer
                                 l’exécution.


    Evolution du nombre des SEGMA relevant du                     Evolution du taux de recouvrement des
     domaine de l'équipement, du transport et                  dépenses par les recettes propres des SEGMA
        autres infrastructures économiques                       relevant du domaine de l'équipement, du
                                                                     transport et autres infrastructures
    19      19
                                                                               économiques




   2018     2019    2020       2021     2022    2023


     Evolution des dépenses et des recettes des                   Evolution de la structure des recettes des
   SEGMA relevant du domaine de l'équipement,                   SEGMA relevant du domaine de l'équipement,
                                                                    du transport et autres infrastructures
                            RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


I.7.SEGMA relevant du domaine des autres actions économiques

Il s’agit du SEGMA chargé de la Privatisation, dont les attributions ainsi que les
réalisations financières durant la période 2018-2023 sont présentées comme suit :

  Libellé des SEGMA_______________________ Attributions des SEGMA
                          ► Réaliser les actions de préparation, de supervision et de mise en oeuvre des
     MINISTERE DE           opérations liées au processus de la privatisation, à savoir :
  L’ECONOMIE ET DES            • Réaliser les audits et les évaluations des sociétés et des entreprises
      FINANCES :            publiques figurant dans le programme de privatisation ;
  SEGMA chargé de la           • Organiser les campagnes promotionnelles de publication, d’impression
      Privatisation         et de communication relatives aux sociétés concernées par la privatisation ;
                               •   Conduire les opérations de restructuration des entreprises publiques.


       Evolution du nombre des SEGMA                   Evolution du taux de recouvrement des
         relevant des autres actions                    dépenses par les recettes propres des
                 économiques                           SEGMA relevant du domaine des autres
                                                                actions économiques


      14




                                                     0%      0%      0%      0%       0%      0%
  PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |



1.8. SEGMA relevant du domaine de l’agriculture et de la pêche maritime
Lesdits SEGMA offrent des prestations liées au domaine de l’eau et de
l’environnement. Ils interviennent principalement dans la protection des ressources
hydriques, halieutiques, forestières et environnementales. Les attributions de ces
SEGMA ainsi que leurs réalisations financières durant la période 2018-2023 peuvent
être présentées ainsi :

    Libellé des SEGMA_______________________ Attributions des SEGMA
        MINISTERE DE
  L'AGRICULTURE, DE LA
    PECHE MARITIME, DU
                                 • Apporter un appui à la recherche halieutique et prendre en charge les
 DEVELOPPEMENT RURAL
                                   opérations de contrôle effectuées par le corps des observateurs scientifiques
 ET DES EAUX ET FORETS :
                                   à bord des navires étrangers.
 Division de la Durabilité et
     Aménagement des
   Ressources Maritimes
                                 • Évaluer et assurer le suivi de la situation de l’environnement en collaboration
                                   avec tous les organes concernés ;
                                 • Entreprendre des études et des recherches sur l’environnement dans le cadre
                                   de la politique nationale du développement durable, et tenir informés les
                                   pouvoirs publics des résultats et des mesures prises pour leur application ;
                                 • Promouvoir et coordonner toutes les actions visant la préservation de
                                   l’équilibre du milieu naturel, la prévention, la lutte contre la pollution et les
                                   nuisances et l’amélioration du cadre de vie ;
     MINISTERE DE LA             • Élaborer les propositions relatives aux principales orientations et stratégies
        TRANSITION                 en matière de politique environnementale, et réaliser les projets pilotes aux
    ENERGETIQUE ET DU              niveaux national, régional et local ;
     DEVELOPPEMENT
                                 • Établir à partir d’informations complètes sur l’état de l’environnement, des
         DURABLE :
                                   inventaires et des diagnostics des problèmes l’affectant ;
  Laboratoire National des
                                 • Recueillir et diffuser toutes les informations relatives à l’environnement ;
  études et de surveillance
       de la pollution           • Assurer le suivi de la coordination interministérielle en matière de protection
                                   de l’environnement ;
                                 • Susciter et participer à l’élaboration et à la mise en place des plans d’urgence
                                   et de suivi ;
                                 • Effectuer des interventions en matière de lutte contre les catastrophes
                                   naturelles ;
                                 • Promouvoir avec les départements ministériels concernés les projets de
                                   coopération internationale dans le domaine de l’environnement, et en assurer
                                   la coordination vis-à-vis des ministères compétents.
                        RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME




Evolution du nombre des SEGMA relevant           Evolution du taux de recouvrement des
du domaine de l'agriculture et de la pêche        dépenses par les recettes propres des
                maritime                       SEGMA relevant du domaine de l'agriculture
      PROJET DE LOI DE FINANCES POUR L’ANNEE 2025 |




ANNEXE 2 : TABLEAU RECAPITULATIF DE L’EXECUTION DES BUDGETS DES SEGMA AU TITRE DES
           ANNEES 2022 ET 2023
                                                                                   ANNEE 2022                                          ANNEE 2023
                                                                                                       Taux de                                            Taux de
                       Désignation                           Prévisions (2)          Réalisations                    Prévisions (4)     Réalisations
                                                                                                      réalisation                                        réalisation
 I- CHARGES (1)
        Exploitation                                        3.900.261.326,53 2.104.529.213,21          53,96%       3.937.419.176,84 2.334.695.778,80     59,30%
        Investissement                                      1.380.839.810,79        462.898.392,49     33,52%       1.328.179.440,40    317.611.971,75    23,91%
TOTAL DES CHARGES                                           5.281.101.137,32 2.567.427.605,70          48,62%       5.265.598.617,24 2.652.307.750,55     50,37%
 II- RESSOURCES
 Subvention d'Exploitation                                    760.876.460,00         765.833.844,00    100,65%       845.450.060,00     822.672.609,00    97,31%
 Subvention d'investissement                                  117.389.000,00         118.802.200,00    101,20%       111.985.000,00      96.254.500,00    85,95%
Total des subventions                                         878.265.460,00         884.636.044,00    100,73%       957.435.060,00     918.927.109,00    95,98%
 Recettes propres (3)                                       1.375.261.257,66 1.685.259.193,97          122,54%      1.374.092.087,82 2.423.991.793,80     176,41%
SOUS TOTAL                                 2.253.526.717,66 2.569.895.237,97                           114,04%      2.331.527.147,82 3.342.918.902,80     143,38%
Excédent des recettes sur les paiements au
                                           3.027.574.419,66 3.190.526.939,74                           105,38%      2.724.380.759,58 3.121.585.427,65     114,58%
titre de la gestion antérieure
 TOTAL DES RESSOURCES (3)                  5.281.101.137,32 5.760.422.177,71                           109,08%      5.055.907.907,40 6.464.504.330,45     127,86%
(1)   Tenant compte de l’affectation de l’excédent de l’exercice antérieur ;
(2)   Prévisions actualisées ;
(3)   Incluent dons et legs ;
(4)   Prévisions actualisées sur la base de la situation communiquée par la TGR au 30/06/2024.
                                                 RAPPORT SUR LES SERVICES DE L’ETAT GERES DE MANIERE AUTONOME


        ANNEXE 3 : EVOLUTION DES RECETTES DES SEGMA EN 2022 ET 2023
                                                             Année 2022                                      Année 2023
                                                                               Taux de                                            Taux de
                                            Prévisions (1)     Réalisations                 Prévisions (1)      Réalisations
                                                                              réalisation                                        réalisation
1- DOMAINE DE LA SANTE
Subvention d'Exploitation                605.056.560,00   606.876.560,00   100,30%  681.356.560,00             674.510.560,00     99,00%
Subvention d'investissement               20.000.000,00    20.000.000,00   100,00%  20.000.000,00               18.000.000,00     90,00%
Total Subventions                        625.056.560,00   626.876.560,00  100,29%   701.356.560,00             692.510.560,00     98,74%
Recettes propres                         775.791.869,00   813.557.863,91   104,87%  797.710.362,30            1.573.514.480,99    197,25%
Excédent du budget d'exploitation       1.062.316.581,64 1.071.533.040,54  100,87%  709.339.866,47             968.129.016,92     136,48%
Excédent du budget d'investissement      169.163.947,17   183.738.103,81   108,62%  158.251.117,40             155.931.997,34     98,53%
Total général des recettes_____________ 2.632.328.957,81 2.695.705.568,26 102,41%  2.366.657.906,17           3.390.086.055,25    143,24%
2- DOMAINE DE L'ENSEIGNEMENT, DE LA FORMATION PROFESSIONNELLE ET DE LA FORMATION DES CADRES
Subvention d'Exploitation                106.229.500,00   105.866.884,00   99,66%   112.119.500,00              98.398.397,00     87,76%
Subvention d'investissement               76.339.000,00    61.752.200,00   80,89%   71.485.000,00              62.754.500,00      87,79%
Total Subventions                        182.568.500,00   167.619.084,00   91,81%   183.604.500,00             161.152.897,00     87,77%
Recettes propres                         127.673.500,00    52.486.626,37   41,11%   119.363.520,00             77.451.970,45      64,89%
Excédent du budget d'exploitation         99.093.557,48    94.485.999,07   95,35%   100.587.279,30              98.419.479,49     97,84%
Excédent du budget d'investissement      229.134.155,52   251.430.518,02   109,73%  234.504.460,53             263.407.906,16     112,33%
Total général des recettes_____________  638.469.713,00   566.022.227,46   88,65%   638.059.759,83             600.432.253,10     94,10%
3- DOMAINE DES ACTIVITES RECREATIVES
Subvention d'Exploitation                 24.000.000,00    27.500.000,00   114,58%  26.000.000,00              23.289.652,00      89,58%
Subvention d'investissement               11.000.000,00    28.000.000,00  254,55%    11.000.000,00              8.000.000,00      72,73%
Total Subventions                         35.000.000,00    55.500.000,00  158,57%   37.000.000,00              31.289.652,00      84,57%
Recettes propres                         40.914.615,00     53.431.718,55   130,59%   35.500.000,00             59.890.801,24      168,71%
Excédent du budget d'exploitation         21.892.852,91    22.290.338,34   101,82%   37.054.345,36             38.253.442,16      103,24%
Excédent du budget d'investissement       13.731.149,93    13.731.149,93   100,00%   31.480.010,80             31.710.010,80      100,73%
Total général des recettes_____________  111.538.617,84   144.953.206,82  129,96%   141.034.356,16             161.143.906,20     114,26%
4- DOMAINE DES AUTRES ACTIONS SOCIALES
Subvention d'Exploitation                      0,00             0,00           -          0,00                      0,00              -
Subvention d'investissement                    0,00             0,00           -          0,00                      0,00              -
Total Subventions                              0,00             0,00           -          0,00                      0,00              -
Recettes propres                         45.500.000,00     66.002.719,99   145,06%  45.500.000,00              33.644.876,51      73,94%
Excédent du budget d'exploitation         63.287.019,27    63.287.019,27   100,00%   83.242.958,00             83.396.478,00      100,18%
Excédent du budget d'investissement        8.471.875,51     8.471.875,51   100,00%   8.348.828,01               8.348.828,01      100,00%
Total général des recettes_____________  117.258.894,78   137.761.614,77  117,49%   137.091.786,01             125.390.182,52     91,46%
5- DOMAINE DES POUVOIRS PUBLICS ET SERVICES GENERAUX
Subvention d'Exploitation                  5.590.400,00     5.590.400,00   100,00%   5.774.000,00               6.274.000,00      108,66%
Subvention d'investissement                6.000.000,00     6.000.000,00   100,00%   6.000.000,00               6.000.000,00      100,00%
Total Subventions                         11.590.400,00    11.590.400,00  100,00%    11.774.000,00              12.274.000,00     104,25%
Recettes propres                         151.447.561,46   299.215.402,01   197,57%  159.018.205,52             312.625.024,31     196,60%
Excédent du budget d'exploitation        457.705.881,99   418.273.161,15   91,38%   524.155.715,49             470.757.663,55     89,81%
Excédent du budget d'investissement      310.361.578,43   301.584.892,55   97,17%   279.546.780,80             269.205.076,73     96,30%
Total général des recettes_____________  931.105.421,88  1.030.663.855,71 110,69%   974.494.701,81            1.064.861.764,59    109,27%
6- DOMAINE DE L’EQUIPEMENT, DU TRANSPORT ET AUTRES INFRASTRUCTURES ECONOMIQUES
Subvention d'Exploitation                      0,00             0,00           -          0,00                      0,00              -
Subvention d'investissement                    0,00             0,00           -          0,00                      0,00              -
Total Subventions                              0,00             0,00           -          0,00                      0,00              -
Recettes propres                         219.916.072,20   380.732.072,19   173,13%  217.000.000,00             366.680.272,54     168,98%
Excédent du budget d'exploitation        228.370.619,93   299.973.922,80   131,35%  270.824.360,09             358.186.030,91     132,26%
Excédent du budget d'investissement      292.024.462,73   338.100.880,37   115,78%  260.622.373,65             315.902.340,13     121,21%
Total général des recettes_____________  740.311.154,86  1.018.806.875,36 137,62%   748.446.733,74            1.040.768.643,58    139,06%
7- DOMAINE DES AUTRES ACTIONS ECONOMIQUES
Subvention d'Exploitation                      0,00             0,00           -          0,00                      0,00              -
Subvention d'investissement                    0,00             0,00           -          0,00                      0,00              -
Total Subventions                              0,00             0,00           -          0,00                      0,00              -
Recettes propres                               0,00             0,00           -          0,00                      0,00              -
Excédent du budget d'exploitation              0,00             0,00           -          0,00                      0,00              -
Excédent du budget d'investissement       25.379.219,62    25.379.219,62   100,00%  25.379.219,62              25.379.219,62      100,00%
Total général des recettes_____________   25.379.219,62    25.379.219,62  100,00%   25.379.219,62              25.379.219,62      100,00%
8- DOMAINE DE L'AGRICULTURE ET DE LA PECHE MARITIME
Subvention d'Exploitation                 20.000.000,00    20.000.000,00   100,00%  20.200.000,00              20.200.000,00      100,00%
Subvention d'investissement               4.050.000,00      3.050.000,00   75,31%    3.500.000,00               1.500.000,00      42,86%
Total Subventions                         24.050.000,00    23.050.000,00   95,84%   23.700.000,00              21.700.000,00       91,56%
Recettes propres                          14.017.640,00    19.832.790,95   141,48%        0,00                   184.367,76           -
Excédent du budget d'exploitation          3.307.095,65    54.912.396,88  1660,44%    636.773,99                2.950.838,85      463,40%
Excédent du budget d'investissement      43.334.421,88     43.334.421,88   100,00%    406.670,07               31.607.098,98     7772,17%
Total général des recettes_____________   84.709.157,53   141.129.609,71  166,60%   24.743.444,06              56.442.305,59      228,11%
Tous domaines confondus
Subvention d'Exploitation                760.876.460,00   765.833.844,00   100,65%  845.450.060,00             822.672.609,00     97,31%
Subvention d'investissement              117.389.000,00   118.802.200,00   101,20%  111.985.000,00              96.254.500,00     85,95%
Total Subventions                        878.265.460,00   884.636.044,00  100,73%   957.435.060,00             918.927.109,00     95,98%
Recettes propres (2)                    1.375.261.257,66 1.685.259.193,97  122,54% 1.374.092.087,82           2.423.991.793,80    176,41%
Excédent du budget d'exploitation       1.935.973.608,87 2.024.755.878,05  104,59% 1.725.841.298,70           2.020.092.949,88    117,05%
Excédent du budget d'investissement     1.091.600.810,79 1.165.771.061,69  106,79%  998.539.460,88            1.101.492.477,77    110,31%
Total général des recettes              5.281.101.137,32 5.760.422.177,71 109,08%  5.055.907.907,40           6.464.504.330,45    127,86%

  (1) Prévisions actualisées (2) Incluent dons et legs
      PROJET DE LOI DE FINANCES POUR L'ANNEE 2024 |




         ANNEXE 4 : EVOLUTION DES DEPENSES DES SEGMA EN 2022 ET 2023

                                               Crédits ouverts     Emissions au          Taux       Crédits ouverts    Emissions au          Taux
Désignation
                                                    2022            31/12/2022        d'exécution        2023           31/12/2023        d’exécution


1- DOMAINE DE LA SANTE

Exploitation                                   2.384.165.010,64    1.520.507.913,61     63,78%      2.360.982.921,53   1.697.351.278,27     71,89%

Investissement                                   248.163.947,17       52.188.413,37     21,03%       248.874.426,97      58.269.279,04      23,41%

TOTAL DU DOMAINE DE LA SANTE                   2.632.328.957,81    1.572.696.326,98     59,75%      2.609.857.348,50   1.755.620.557,31     67,27%

2- DOMAINE DE L'ENSEIGNEMENT, DE LA FORMATION PROFESSIONNELLE ET DE LA FORMATION DES CADRES

Exploitation                                     326.146.557,48      145.359.040,54     44,57%       324.026.940,98     159.608.874,02      49,26%

Investissement                                   312.323.155,52       65.455.905,96     20,96%       314.478.007,83      74.703.172,98      23,75%
TOTAL DU DOMAINE DE L'ENSEIGNEMENT,
DE LA FORMATION PROFESSIONNELLE ET               638.469.713,00     210.814.946,50      33,02%       638.504.948,81     234.312.047,00      36,70%
DE LA FORMATION DES CADRES
3- DOMAINE DES ACTIVITES RECREATIVES

Exploitation                                      86.807.467,91       64.738.614,73     74,58%       103.616.978,46      76.678.828,40      74,00%

Investissement                                    24.731.149,93       10.251.139,13     41,45%        42.710.010,80       10.922.701,30     25,57%
TOTAL DU DOMAINE DES ACTIVITES
                                                 111.538.617,84       74.989.753,86     67,23%       146.326.989,26      87.601.529,70      59,87%
RECREATIVES
4- DOMAINE DES AUTRES ACTIONS SOCIALES

Exploitation                                     108.787.019,27       45.893.261,26     42,19%       128.742.958,00      77.095.631,28      59,88%

Investissement                                     8.471.875,51          123.047,50     1,45%           8.348.828,01        206.447,60      2,47%
TOTAL DU DOMAINE DES AUTRES
                                                 117.258.894,78       46.016.308,76     39,24%       137.091.786,01      77.302.078,88      56,39%
ACTIONS SOCIALES_____________________
5- DOMAINE DES POUVOIRS PUBLICS ET SERVICES GENERAUX

Exploitation                                     614.743.843,45      177.943.406,69     28,95%       624.798.149,26     175.525.013,74      28,09%

Investissement                                   316.361.578,43      112.761.486,58     35,64%       285.951.338,70      67.095.286,35      23,46%
TOTAL DU DOMAINE DES POUVOIRS
                                                 931.105.421,88     290.704.893,27      31,22%       910.749.487,96     242.620.300,09      26,64%
PUBLICS ET SERVICES GENERAUX________
6- DOMAINE DE L’EQUIPEMENT, DU TRANSPORT ET AUTRES INFRASTRUCTURES ECONOMIQUES

Exploitation                                     342.286.692,13      126.282.451,23     36,89%       372.100.389,76     128.633.271,69      34,57%

Investissement                                   398.024.462,73     207.399.927,21      52,11%       367.330.509,49     103.299.247,62      28,12%
TOTAL DU DOMAINE DE L’EQUIPEMENT,
DU TRANSPORT ET AUTRES                           740.311.154,86     333.682.378,44      45,07%       739.430.899,25     231.932.519,31      31,37%
INFRASTRUCTURES ECONOMIQUES_______
7- DOMAINES DES AUTRES ACTIONS ECONOMIQUES

Exploitation                                               0,00                0,00        -                    0,00               0,00        -

Investissement                                    25.379.219,62                0,00     0,00%         25.379.219,62                0,00     0,00%
TOTAL DU DOMAINE DES AUTRES
                                                  25.379.219,62                0,00     0,00%         25.379.219,62                0,00     0,00%
ACTIONS ECONOMIQUES_________________
8- DOMAINE DE L'AGRICULTURE ET DE LA PECHE MARITIME

Exploitation                                      37.324.735,65       23.804.525,15     63,78%        23.150.838,85       19.802.881,40     85,54%

Investissement                                    47.384.421,88       14.718.472,74     31,06%        35.107.098,98        3.115.836,86     8,88%
TOTAL DU DOMAINE DE L'AGRICULTURE
                                                  84.709.157,53       38.522.997,89     45,48%        58.257.937,83      22.918.718,26      39,34%
ET DE LA PECHE MARITIME_______________
Tous domaines confondus

Exploitation                                   3.900.261.326,53    2.104.529.213,21     53,96%      3.937.419.176,84   2.334.695.778,80     59,30%

Investissement                                 1.380.839.810,79     462.898.392,49      33,52%      1.328.179.440,40    317.611.971,75      23,91%

TOTAL GENERAL (1)                              5.281.101.137,32    2.567.427.605,70     48,62%      5.265.598.617,24   2.652.307.750,55     50,37%


(1)   Tenant compte de l’affectation de l’excédent de l’exercice antérieur
        
"""
    conversation_history = StreamlitChatMessageHistory()  # Créez l'instance pour l'historique

    st.header("PLF2025: Explorez le rapport sur les services de l'état gérés de manière autonome à travers notre chatbot 💬")
    
    # Load the document
    #docx = 'PLF2025-Rapport-FoncierPublic_Fr.docx'
    
    #if docx is not None:
        # Lire le texte du document
        #text = docx2txt.process(docx)
        #with open("so.txt", "w", encoding="utf-8") as fichier:
            #fichier.write(text)

        # Afficher toujours la barre de saisie
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)
    selected_questions = st.sidebar.radio("****Choisir :****", questions)
        # Afficher toujours la barre de saisie
    query_input = st.text_input("", key="text_input_query", placeholder="Posez votre question ici...", help="Posez votre question ici...")
    st.markdown('<div class="input-space"></div>', unsafe_allow_html=True)

    if query_input and query_input not in st.session_state.previous_question:
        query = query_input
        st.session_state.previous_question.append(query_input)
    elif selected_questions:
        query = selected_questions
    else:
        query = ""

    if query :
        st.session_state.conversation_history.add_user_message(query) 
        if "Donnez-moi un résumé du rapport" in query:
            summary="""Le document est une note explicative du Projet de Loi de Finances (PLF) pour l’année 2025, se concentrant sur les dépenses relatives aux charges communes. Il présente les grandes orientations budgétaires, les priorités de financement et la répartition des dépenses pour couvrir les besoins communs de l’État. Ce projet vise à optimiser l’utilisation des ressources publiques, en soutenant des initiatives prioritaires dans divers secteurs, comme l’éducation, la santé, et le développement social. Le document souligne également les efforts pour renforcer la transparence et l’efficacité budgétaire afin de répondre aux enjeux socio-économiques du pays pour l’année à venir."""
            st.session_state.conversation_history.add_ai_message(summary) 

        else:
            messages = [
                {
                    "role": "user",
                    "content": (
                        f"{query}. Répondre à la question d'apeés ce texte repondre justement à partir de texte ne donne pas des autre information voila le texte donnee des réponse significatif et bien formé essayer de ne pas dire que information nest pas mentionné dans le texte si tu ne trouve pas essayer de repondre dapres votre connaissance ms focaliser sur ce texte en premier: {text} "
                    )
                }
            ]

            # Appeler l'API OpenAI pour obtenir le résumé
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )

            # Récupérer le contenu de la réponse

            summary = response['choices'][0]['message']['content']
           
                # Votre logique pour traiter les réponses
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(response)
            st.session_state.conversation_history.add_ai_message(summary)  # Ajouter à l'historique
            
            # Afficher la question et le résumé de l'assistant
            #conversation_history.add_user_message(query)
            #conversation_history.add_ai_message(summary)

            # Format et afficher les messages comme précédemment
                
            # Format et afficher les messages comme précédemment
        formatted_messages = []
        previous_role = None 
        if st.session_state.conversation_history.messages: # Variable pour stocker le rôle du message précédent
                for msg in conversation_history.messages:
                    role = "user" if msg.type == "human" else "assistant"
                    avatar = "🧑" if role == "user" else "🤖"
                    css_class = "user-message" if role == "user" else "assistant-message"

                    if role == "user" and previous_role == "assistant":
                        message_div = f'<div class="{css_class}" style="margin-top: 25px;">{msg.content}</div>'
                    else:
                        message_div = f'<div class="{css_class}">{msg.content}</div>'

                    avatar_div = f'<div class="avatar">{avatar}</div>'
                
                    if role == "user":
                        formatted_message = f'<div class="message-container user"><div class="message-avatar">{avatar_div}</div><div class="message-content">{message_div}</div></div>'
                    else:
                        formatted_message = f'<div class="message-container assistant"><div class="message-content">{message_div}</div><div class="message-avatar">{avatar_div}</div></div>'
                
                    formatted_messages.append(formatted_message)
                    previous_role = role  # Mettre à jour le rôle du message précédent

                messages_html = "\n".join(formatted_messages)
                st.markdown(messages_html, unsafe_allow_html=True)
if __name__ == '__main__':
    main()
