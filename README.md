**PROJECT DEVIN LEE**
---
**TITLE**  
*Landslide-Factors-of-risk-in-Iran using-Airflow*

---
**DATASET**  

*This dataset was created by Mohammad Rahdan, which contains information and factors that affect the occurrence of landslides in Iran. This dataset contains more than 4000 landslide hazard zones, where each of these zones has certain factors that can trigger landslides. These factors include slope, climate, tectonic activity and so on. Is there even a human-induced factor.*

---
**OBJECTIVES**  
*The purpose of this analysis is to find out what factors can trigger the occurrence of landslides, and what suggestions will be given to avoid or minimize the occurrence of landslides or at least not take casualties.*

---

**TOOLS**  
```py
import sqlalchemy as db
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import re
import warnings
from great_expectations.data_context import FileDataContext
import plotly.express as px
```

**DATASET SOURCE** : [Kaggle](https://www.kaggle.com/datasets/mohammadrahdanmofrad/landslide-risk-assessment-factors)