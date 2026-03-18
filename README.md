# Group_J
Advanced Programming Project - Group J

Group members:  
    - Aléxia Sousa: 51894@novasbe.pt  
    - Giacomo Castiglioni: 73411@novasbe.pt  
    - Liane Kpocheme: 73516@novasbe.pt  
    - Simone Capata: 74777@novasbe.pt  

## Prerequisites

Before setting up the environment, make sure you have the following installed:

- ⁠[Conda](https://docs.conda.io/en/latest/miniconda.html)
- [Ollama](https://ollama.com/download): required for the AI Workflow page

After installing Ollama, make sure it is running before launching the app:
```
ollama serve
```

## Setup (Recommended)
To create the conda environment:
```
conda env create -f environment.yml
conda activate requirements_j
```

To update the conda environment:
```
conda env update -f environment.yml --prune
```

Run the Streamlit app:
```
streamlit run app/1_Environmental_Explorer.py
streamlit run app/pages/2_AI_Risk_Analysis.py
```
⁠> ***Note:** Make sure Ollama is running (⁠ ollama serve ⁠) before launching Page 2 of the app.*



Run tests:
```
pytest -q
```
## 🌍 Impact on the UN Sustainable Development Goals (SDGs)

This project was designed with a clear vision: to democratize environmental monitoring by combining accessible satellite imagery with local, privacy-preserving Artificial Intelligence. By automating the detection of ecological threats, this application directly contributes to several of the **United Nations' Sustainable Development Goals (SDGs)**:

* **[Goal 15: Life on Land](https://sdgs.un.org/goals/goal15)** 🌳
  This is the primary focus of our application. By analyzing high-resolution ESRI satellite tiles, the AI can rapidly identify signs of deforestation, illegal logging, and land degradation. Providing an accessible tool to monitor forest cover changes empowers NGOs, local governments, and researchers to protect vital ecosystems and halt biodiversity loss without needing expensive cloud-computing infrastructure.

* **[Goal 13: Climate Action](https://sdgs.un.org/goals/goal13)** 🌡️
  Forests are our most crucial carbon sinks. By acting as an early warning system for environmental degradation, this tool helps communities respond faster to climate-related hazards (such as rapidly drying water bodies or expanding desertification), integrating vital data into climate change planning and mitigation strategies.

* **[Goal 11: Sustainable Cities and Communities](https://sdgs.un.org/goals/goal11)** 🏙️
  The application isn't just for wild areas; it can also analyze urban environments. By inputting city coordinates, the AI can assess the balance between concrete infrastructure and green spaces, helping urban planners recognize the environmental risks of uncontrolled expansion and work toward more inclusive and sustainable urbanization.

Ultimately, by relying on local AI models (`moondream` and `llama3.2:1b`), this project ensures that environmental protection tools are sustainable, low-cost, and accessible even to communities with limited internet bandwidth, bridging the technological divide in ecological preservation.

---

## 🚨 AI Risk Identification Showcase

Below are three real-world examples demonstrating the application's ability to analyze coordinates, describe the landscape, and successfully flag environmental dangers.

### Example 1: Active Deforestation (Amazon Rainforest)
* **Coordinates:** Lat -9.36, Lon -63.00 (Zoom 15)
* **Risk Level:** 🔴 High

 
**AI Vision Description:** The image presents an aerial view of a densely forested area. The predominant color scheme is green, indicating the presence of vegetation such as trees and bushes covering most of the landscape. There are also some visible water bodies in the vicinity, suggesting that this region might be near a river or lake. Additionally, there are roads and buildings scattered throughout the scene, which could potentially indicate human activity in the area. The image also contains signs of deforestation, erosion, flooding, pollution, or land degradation, indicating possible environmental concerns related to the management and preservation of this lush green landscape.

**AI Risk Assessment:** 
- Main Risks: Forests (deforestation), Arid regions (desertification)

- Explanation: The image detects widespread deforestation in Brazil's forested areas, which is a clear indication of environmental degradation. This trend is particularly concerning given the country's known large-scale forest loss and the increasing frequency of wildfires associated with it. Additionally, the region's arid characteristics pose significant risks to ecosystems that are not adapted to such conditions, such as soil erosion and potential desertification in sensitive areas like the Amazon rainforest.

### Example 2: Urban Environment & Coastal Monitoring (Lisbon, Portugal)
* **Coordinates:** Lat 38.72, Lon -9.14 (Zoom 15)
* **Risk Level:** 🟡 Medium 


 **AI Vision Description:** The satellite image shows an aerial view of a densely populated city with numerous buildings in shades of orange and brown. The streets are lined with trees, indicating the presence of green spaces within the urban environment. A few small water bodies can be seen near some of the buildings, suggesting that the city is situated close to a water source or a river. The image also highlights several signs of environmental concerns such as deforestation, flooding, erosion, and pollution. The dense concentration of buildings in the area could potentially lead to increased air and noise pollution due to vehicular traffic and industrial activities. Additionally, the presence of trees near the streets might indicate that some areas are experiencing land degradation or loss of vegetation cover. Overall, the image presents a complex urban landscape with both positive aspects like green spaces and water bodies, as well as negative environmental concerns that need to be addressed for sustainable development.
 
 **AI Risk Assessment:** 
- Main Risks: Forests (deforestation), Urban sprawl, Air and water pollution

- Explanation: The densely populated city highlights the potential for deforestation and urban sprawl, which can lead to increased greenhouse gas emissions, loss of biodiversity, and negative impacts on air quality. Additionally, the presence of green spaces within the urban environment could be eroded as the city grows, contributing to air and noise pollution due to vehicular traffic and industrial activities. The overall image suggests that sustainable development in this region may require careful planning and mitigation strategies to balance economic growth with environmental protection.

### Example 3: Severe Land Degradation (Bingham Canyon Mine, USA)
* **Coordinates:** Lat 40,52, Lon -112,15 (Zoom 15)
* **Risk Level:** 🟡 Medium 



**AI Vision Description:** The satellite image shows an aerial view of a large open area that appears to be a coal mine or industrial site. The landscape features numerous hills and valleys, indicating the presence of mountains in the background. The terrain is predominantly covered in dirt and bare soil, with some vegetation scattered throughout. There are also several roads and buildings within the scene, suggesting human activity and infrastructure development around the area. The image highlights potential environmental concerns such as deforestation, flooding, erosion, or pollution resulting from industrial activities. These issues can have a significant impact on the surrounding ecosystem and may require careful planning and management to minimize their effects on the environment and local communities.


**AI Risk Assessment:**
- Main Risks: Deforestation, Water Pollution, Human Settlement Impact, Air Quality Issues

- Explanation: The presence of an industrial site in a previously undeveloped area suggests potential for deforestation due to clear-cutting for coal production or other extractive activities. Additionally, the lack of country-level statistics makes it difficult to assess the overall impact on the region's ecosystem, but the image does not show any obvious signs of pollution or waste management issues that would classify this as a certain danger. The human settlement around the area and potential infrastructure development suggest that water quality may be impacted by industrial activities, such as wastewater or sewage. Furthermore, air quality could be affected by emissions from industrial sites, leading to concerns about local health and well-being.
