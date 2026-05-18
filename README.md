# final-project-uni
My final project for university, entitled 'Creation and Exploration of Informal Guidelines for Implementing RoboChart Models in ROS 2'.

# Executive Summary
Robots are increasingly being used in safety-critical applications, so it is more important than ever to ensure they behave correctly and safely. Modelling can be used to reason out and test behaviour before implementing it, which generally leads to better thought-out solutions. This means that robots should be safer and more consistent. An architect wouldn’t start making a building before designing it in detail, so why should a roboticist?
This project aims to create a set of guidelines for taking a testable, wellreasoned model and implementing it. During implementation, no details of the model can slip through the cracks or be misunderstood; otherwise, all the effort of creating the model is wasted.
There is an introduction to RoboChart, ROS 2, and other key concepts, followed by an exploration of different modelling languages and middleware, culminating in the decision to use RoboChart and ROS 2. Previous similar work is discussed before heading into planning how the project will be carried out, where it is revealed that an agile development style was employed to create the guidelines.
Seven success criteria are set: "SRanger RoboChart model implemented.", "SRanger runs in a ROS environment.", "Initial Guidelines created.", "Alpha Algorithm RoboChart model implemented.", "Guidelines updated to final version.", "Guidelines are coherent and easy to follow.", "Guidelines cover a good proportion of the RoboChart language". After that, a run-through of key RoboChart concepts takes place, planning how they will fit into a ROS implementation before heading into the meat of the matter. The report goes through the entire process of creating a ROS implementation from the RoboChart model known as ’SRanger’. Once the in-depth exploration of this model and translation has taken place, there will be a quick discussion of simulating the SRanger implementation. Any thoughts and ideas from the process so far have been distilled into a set of guidelines that anyone should be able to follow to create their own ROS implementation from a RoboChart model.
These guidelines are then put to the test by creating a second implementation, this time for the RoboChart model ’Alpha Algorithm’. Any issues or missing pieces are noted along the way, and the guidelines are edited at
v
Executive Summary
the end of the process.
There is a quick evaluation of the case study implementations themselves,
followed by a qualitative analysis of the guidelines, including experiences
of how easy it was to follow them.
The Success criteria are evaluated before the project concludes with the
main aim completed, all of the success criteria at least mostly completed,
and a solid set of guidelines created from it all.
