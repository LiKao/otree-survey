=====
oTree Survey App
=====

A simple app to create surveys using XML definitions within oTree.


Quick start
-----------

1. Add "otreesurvey" to INSTALLED_APPS:
  INSTALLED_APPS = {
    ...
    'otreesurvey'
  }
2. Create an otree app where this survey should be used
3. Import the survey module in the models.py and define a Survey object
  from otreesurvey import Survey
  survey = Survey( "Appname", "Survey.xml")
4. Make sure that the number of rounds matches the number of pages in the survey:
  class Constants(BaseConstants):
     name_in_url = 'Appname'
     players_per_group = None
     num_rounds = survey.num_rounds
5. Replace the Player class with one generated based on the definition
  Player = survey.create_player()
6. Import the survey definition in views.py
  from .models import survey
7. Generate the view from the survey definition
  SurveyPage = survey.create_page()
8. Make sure page_sequence only includes the generated SurveyPage
  page_sequence = [SurveyPage]
