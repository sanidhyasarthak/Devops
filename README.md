
## Overview
This project demonstrates the power of **Machine Learning** and **Genetic Algorithms** by training an Artificial Neural Network to autonomously navigate a dynamically generated obstacle course. 

Instead of hard-coding the rules of flight, this program uses the **NEAT (NeuroEvolution of Augmenting Topologies)** algorithm. The AI begins with zero knowledge of physics or mechanics. Through iterative generations of random mutation, fitness evaluation, and selective breeding, the computer slowly evolves a flawless neural brain capable of endless survival.

## How the AI Works
The project mimics biological evolution:
1. **Population Initialization:** A population of neural networks (birds) is spawned into the environment. 
2. **Inputs (Sensors):** Each network is fed 3 precise data points every frame:
   - The entity's current Y-Axis position.
   - The distance to the top obstacle.
   - The distance to the bottom obstacle.
3. **Fitness Function:** The longer an entity survives and moves forward, the higher its "Fitness Score."
4. **Crossover & Mutation:** When all entities in a generation fail, the algorithm selects the highest-scoring networks, mutates their internal weights/biases, and breeds them to create the next, smarter generation.