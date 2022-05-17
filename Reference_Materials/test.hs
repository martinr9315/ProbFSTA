-- import Test.QuickCheck
import Control.Applicative ((<$>), (<*>), liftA, liftA2, liftA3)
import qualified Data.Map as M
import qualified Data.List as List
import ProbFSTA
import OverUnder


treesets_debugging::[Tree]
treesets_debugging = [Branching "*" [Branching "*" [Leaf "C",Leaf "B"],Leaf "A"],
             Branching "*" [Leaf "A",Branching "*" [Leaf "B",Leaf "C"]],
             Branching "*" [Branching "*" [Leaf "C",Leaf "B"],Leaf "A"]]

tree1 = Branching "*" [Branching "*" [Leaf "C",Leaf "B"],Leaf "A"]


initial_debugging::ProbFSTA
initial_debugging = ([(0, 0.67),(1, 0.33)],
  [((0, "*", [0, 1]), 0.5),
  ((0, "*", [0, 0]), 0.4),
  ((0, "*", [1, 0]), 0.02),
  ((0, "*", [1, 1]), 0.03),
  ((0, "A", []), 0.03),
  ((0, "B", []), 0.02), 
  ((1, "C", []), 1)],
 [0, 1])

-- overValue initial_debugging (getCxt tree1 [1]) 1
-- overValueNoOrder initial_debugging (getCxt tree1 [1]) 1

--update' initial_debugging treesets_debugging
--(([(0,1.0),(1,0.0)],[((0,"*",[0,0]),0.25),((0,"*",[0,1]),8.333333333333333e-2),((0,"*",[1,0]),0.16666666666666666),((0,"*",[1,1]),0.0),((0,"A",[]),0.25),((0,"B",[]),0.25),((0,"C",[]),0.0),((1,"*",[0,0]),0.0),((1,"*",[0,1]),0.0),((1,"*",[1,0]),0.0),((1,"*",[1,1]),0.0),((1,"A",[]),0.0),((1,"B",[]),0.0),((1,"C",[]),1.0)],[0,1]),8.830317744502314e-9)

-- updateN 50 initial_debugging treesets_debugging
--([(0,1.0),(1,0.0)],[((0,"*",[0,0]),0.25),((0,"*",[0,1]),8.333333333333333e-2),((0,"*",[1,0]),0.16666666666666666),((0,"*",[1,1]),0.0),((0,"A",[]),0.25),((0,"B",[]),0.25),((0,"C",[]),0.0),((1,"*",[0,0]),0.0),((1,"*",[0,1]),0.0),((1,"*",[1,0]),0.0),((1,"*",[1,1]),0.0),((1,"A",[]),0.0),((1,"B",[]),0.0),((1,"C",[]),1.0)],[0,1])



initialNO_debugging::ProbFSTA
initialNO_debugging = ([(0, 0.67),(1, 0.33)],
  [((0, "*", [0, 0]), 0.4),
  ((0, "*", [0, 1]), 0.52),
  ((0, "*", [1, 1]), 0.03),
  ((0, "A", []), 0.03),
  ((0, "B", []), 0.02), 
  ((1, "C", []), 1)],
 [0, 1])



-- updateNoOrder initialNO_debugging treesets_debugging
--([(0,1.0),(1,0.0)],[((0,"*",[0,0]),0.25),((0,"*",[0,1]),0.25),((0,"*",[1,1]),0.0),((0,"A",[]),0.25),((0,"B",[]),0.25),((0,"C",[]),0.0),((1,"*",[0,0]),0.0),((1,"*",[0,1]),0.0),((1,"*",[1,1]),0.0),((1,"A",[]),0.0),((1,"B",[]),0.0),((1,"C",[]),1.0)],[0,1])