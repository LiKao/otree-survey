from .QuestionType import QuestionTypeUndefined

from .QuestionType import QuestionType

from .RadioQuestion 	import RadioQuestion
from .SelectQuestion 	import SelectQuestion
from .ButtonQuestion 	import ButtonQuestion
from .TextQuestion 		import TextQuestion
from .ScaleQuestion		import ScaleQuestion

QuestionType.register("radio", 		RadioQuestion)
QuestionType.register("selection", 	SelectQuestion)
QuestionType.register("dropdown", 	SelectQuestion)
QuestionType.register("button", 	ButtonQuestion)
QuestionType.register("text", 		TextQuestion)
QuestionType.register("textfield", 	TextQuestion)
QuestionType.register("scale",		ScaleQuestion)
QuestionType.register("likert",		ScaleQuestion)