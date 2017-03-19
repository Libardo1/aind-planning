# Research Review

`STRIPS` [@fikes1971strips] is the first major automated planning system. It stands for Stanford Research Institute Problem Solver and it was developed by Richard Fikes and Nils Nilsson in 1971 at `SRI International`. `STRIPS` is the controlling component of the robot [`Shakey`](https://upload.wikimedia.org/wikipedia/commons/0/0c/SRI_Shakey_with_callouts.jpg) capable of:

- traveling to another location
- turning light switches on and off
- opening and closing doors
- climbing up and down from rigid objects
- moving objects

Additionally, the authors of `STRIPS` introduced a formal planning language that was used as input for the planner. One `STRIPS` instance consists of initial state, a specification of the goal states and actions. Each action has preconditions and postconditions.

The complexity of deciding whether any plan exists for a propositional STRIPS instance has been shown to be PSPACE-complete [@bylander1994computational]. Further restrictions can be enforced to make it an NP-complete problem.

The impact of `STRIPS` throughout the AI community was really substantial. Even recent games, like F.E.A.R [@orkin2006three], use very similar planning systems.

The approach used by `STRIPS` and similar systems (called `linear programming`) was found to be incomplete and it couldn't solve some very simple problems [@sussman1975computer]. A complete planner must allow for interleaving of actions from different sub-plans within a single sequence.

One solution to this problem was proposed by Waldinger [@waldinger1981achieving]. `Goal regression` constructs totally ordered plan and then constructively modifies it to satisfy all sub-goals. This approach was implemented in the planning system `WARPLAN`. This planner was the first who was written in a logic programming language (Prolog). 

Note that `WARPLAN` still produced its plans as a linear sequence of actions. Non-linear planners like NOAH [@sacerdoti1975nonlinear] dealt with interactions between sub-goals in plans that are partially ordered.

`SatPlan` [@kautz1992planning] tries to cast the problem of planning as one of satisfiability. It converts the planning problem into a Boolean satisfiability problem. What is a satisfiability problem? Given a Boolean formula in conjunctive normal form (CNF), find an
assignment of truth values to literals that makes it true. Intuitively, `SatPlan` constructs a propositional sentence that includes: initial state, set of actions and a goal. Then a SAT solver is called to create a model based on the sentence. It extracts variables that represent actions and creates a plan from them if a model can be constructed.

# References
