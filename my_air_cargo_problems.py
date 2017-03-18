from aimacode.logic import PropKB
from aimacode.planning import Action
from aimacode.search import (
    Node, Problem,
)
from aimacode.utils import expr
from lp_utils import (
    FluentState, encode_state, decode_state,
)
from my_planning_graph import PlanningGraph


class AirCargoProblem(Problem):
    def __init__(self, cargos, planes, airports, initial: FluentState, goal: list):
        """

        :param cargos: list of str
            cargos in the problem
        :param planes: list of str
            planes in the problem
        :param airports: list of str
            airports in the problem
        :param initial: FluentState object
            positive and negative literal fluents (as expr) describing initial state
        :param goal: list of expr
            literal fluents required for goal test
        """
        self.state_map = initial.pos + initial.neg
        self.initial_state_TF = encode_state(initial, self.state_map)
        Problem.__init__(self, self.initial_state_TF, goal=goal)
        self.cargos = cargos
        self.planes = planes
        self.airports = airports
        self.actions_list = self.get_actions()

    def get_actions(self):
        '''
        This method creates concrete actions (no variables) for all actions in the problem
        domain action schema and turns them into complete Action objects as defined in the
        aimacode.planning module. It is computationally expensive to call this method directly;
        however, it is called in the constructor and the results cached in the `actions_list` property.

        Returns:
        ----------
        list<Action>
            list of Action objects
        '''
        def _create_load_action(cargo, plane, airport):
            pre_pos = [expr(f"At({cargo}, {airport})"),
                       expr(f"At({plane}, {airport})")]
            pre_neg = []
            effect_add = [expr(f"In({cargo}, {plane})")]
            effect_neg = [expr(f"At({cargo}, {airport})")]

            return Action(expr(f"Load({cargo}, {plane}, {airport})"),
                          [pre_pos, pre_neg],
                          [effect_add, effect_neg])

        def _create_unload_action(cargo, plane, airport):
            pre_pos = [expr(f"At({cargo}, {airport})"),
                       expr(f"At({plane}, {airport})")]
            pre_neg = []
            effect_add = [expr(f"At({cargo}, {airport})")]
            effect_neg = [expr(f"In({cargo}, {plane})")]

            return Action(expr(f"Unload({cargo}, {plane}, {airport})"),
                          [pre_pos, pre_neg],
                          [effect_add, effect_neg])

        def load_actions():
            '''Create all concrete Load actions and return a list

            :return: list of Action objects
            '''
            loads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        loads.append(_create_load_action(c, p, a))
            return loads

        def unload_actions():
            '''Create all concrete Unload actions and return a list

            :return: list of Action objects
            '''
            unloads = []
            for c in self.cargos:
                for p in self.planes:
                    for a in self.airports:
                        unloads.append(_create_unload_action(c, p, a))
            return unloads

        def fly_actions():
            '''Create all concrete Fly actions and return a list

            :return: list of Action objects
            '''
            flys = []
            for fr in self.airports:
                for to in self.airports:
                    if fr != to:
                        for p in self.planes:
                            precond_pos = [expr("At({}, {})".format(p, fr)),
                                           ]
                            precond_neg = []
                            effect_add = [expr("At({}, {})".format(p, to))]
                            effect_rem = [expr("At({}, {})".format(p, fr))]
                            fly = Action(expr("Fly({}, {}, {})".format(p, fr, to)),
                                         [precond_pos, precond_neg],
                                         [effect_add, effect_rem])
                            flys.append(fly)
            return flys

        return load_actions() + unload_actions() + fly_actions()

    def actions(self, state: str) -> list:
        """ Return the actions that can be executed in the given state.

        :param state: str
            state represented as T/F string of mapped fluents (state variables)
            e.g. 'FTTTFF'
        :return: list of Action objects
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        return [a for a in self.actions_list if a.check_precond(kb, a.args)]

    def result(self, state: str, action: Action):
        """ Return the state that results from executing the given
        action in the given state. The action must be one of
        self.actions(state).

        :param state: state entering node
        :param action: Action applied
        :return: resulting state after action
        """
        old_state = decode_state(state, self.state_map)
        pos, neg = set(old_state.pos), set(old_state.neg)
        pos = pos - set(action.effect_rem)
        neg = neg - set(action.effect_add)
        pos = pos.union(set(action.effect_add))
        neg = neg.union(set(action.effect_rem))
        return encode_state(FluentState(pos, neg), self.state_map)

    def goal_test(self, state: str) -> bool:
        """ Test the state to see if goal is reached

        :param state: str representing state
        :return: bool
        """
        kb = PropKB()
        kb.tell(decode_state(state, self.state_map).pos_sentence())
        for clause in self.goal:
            if clause not in kb.clauses:
                return False
        return True

    def h_1(self, node: Node):
        # note that this is not a true heuristic
        h_const = 1
        return h_const

    def h_pg_levelsum(self, node: Node):
        '''
        This heuristic uses a planning graph representation of the problem
        state space to estimate the sum of all actions that must be carried
        out from the current state in order to satisfy each individual goal
        condition.
        '''
        # requires implemented PlanningGraph class
        pg = PlanningGraph(self, node.state)
        pg_levelsum = pg.h_levelsum()
        return pg_levelsum

    def h_ignore_preconditions(self, node: Node):
        '''
        This heuristic estimates the minimum number of actions that must be
        carried out from the current state in order to satisfy all of the goal
        conditions by ignoring the preconditions required for an action to be
        executed.
        '''
        kb = PropKB()
        kb.tell(decode_state(node.state, self.state_map).pos_sentence())
        return sum(c not in kb.clauses for c in self.goal)


def air_cargo_p1() -> AirCargoProblem:
    cargos = ['C1', 'C2']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO']
    pos = [expr('At(C1, SFO)'),
           expr('At(C2, JFK)'),
           expr('At(P1, SFO)'),
           expr('At(P2, JFK)'),
           ]
    neg = [expr('At(C2, SFO)'),
           expr('In(C2, P1)'),
           expr('In(C2, P2)'),
           expr('At(C1, JFK)'),
           expr('In(C1, P1)'),
           expr('In(C1, P2)'),
           expr('At(P1, JFK)'),
           expr('At(P2, SFO)'),
           ]
    init = FluentState(pos, neg)
    goal = [expr('At(C1, JFK)'),
            expr('At(C2, SFO)'),
            ]
    return AirCargoProblem(cargos, planes, airports, init, goal)

def in_e(arg1, arg2):
    return expr(f"In({arg1}, {arg2})")

def at_e(arg1, arg2):
    return expr(f"At({arg1}, {arg2})")

def air_cargo_p2() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3']
    planes = ['P1', 'P2', 'P3']
    airports = ['JFK', 'SFO', 'ATL']
    pos = [at_e('C1', 'SFO'),
           at_e('C2', 'JFK'),
           at_e('C3', 'ATL'),
           at_e('P1', 'SFO'),
           at_e('P2', 'JFK'),
           at_e('P3', 'ATL')]
    neg = [at_e('C2', 'SFO'),
           at_e('C2', 'ATL'),
           in_e('C2', 'P1'),
           in_e('C2', 'P2'),
           in_e('C2', 'P3'),
           at_e('C1', 'JFK'),
           at_e('C1', 'ATL'),
           in_e('C1', 'P1'),
           in_e('C1', 'P2'),
           in_e('C1', 'P3'),
           at_e('C3', 'JFK'),
           at_e('C3', 'SFO'),
           in_e('C3', 'P1'),
           in_e('C3', 'P2'),
           in_e('C3', 'P3'),
           at_e('P1', 'JFK'),
           at_e('P1', 'ATL'),
           at_e('P2', 'SFO'),
           at_e('P2', 'ATL'),
           at_e('P3', 'JFK'),
           at_e('P3', 'SFO')]
    init = FluentState(pos, neg)
    goal = [at_e('C1', 'JFK'),
            at_e('C2', 'SFO'),
            at_e('C3', 'SFO')]
    return AirCargoProblem(cargos, planes, airports, init, goal)


def air_cargo_p3() -> AirCargoProblem:
    cargos = ['C1', 'C2', 'C3', 'C4']
    planes = ['P1', 'P2']
    airports = ['JFK', 'SFO', 'ATL', 'ORD']
    pos = [at_e('C1', 'SFO'),
           at_e('C2', 'JFK'),
           at_e('C3', 'ATL'),
           at_e('C4', 'ORD'),
           at_e('P1', 'SFO'),
           at_e('P2', 'JFK')]
    neg = [at_e('C2', 'SFO'),
           at_e('C2', 'ATL'),
           at_e('C2', 'ORD'),
           in_e('C2', 'P1'),
           in_e('C2', 'P2'),
           at_e('C1', 'JFK'),
           at_e('C1', 'ATL'),
           at_e('C1', 'ORD'),
           in_e('C1', 'P1'),
           in_e('C1', 'P2'),
           at_e('C3', 'JFK'),
           at_e('C3', 'SFO'),
           at_e('C3', 'ORD'),
           in_e('C3', 'P1'),
           in_e('C3', 'P2'),
           at_e('C4', 'JFK'),
           at_e('C4', 'SFO'),
           at_e('C4', 'ATL'),
           in_e('C4', 'P1'),
           in_e('C4', 'P2'),
           at_e('P1', 'JFK'),
           at_e('P1', 'ATL'),
           at_e('P1', 'ORD'),
           at_e('P2', 'SFO'),
           at_e('P2', 'ATL'),
           at_e('P2', 'ORD')]
    init = FluentState(pos, neg)
    goal = [at_e('C1', 'JFK'),
            at_e('C2', 'SFO'),
            at_e('C3', 'JFK'),
            at_e('C4', 'SFO')]
    return AirCargoProblem(cargos, planes, airports, init, goal)
