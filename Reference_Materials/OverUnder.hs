{-# LANGUAGE TypeSynonymInstances, FlexibleInstances #-}

module OverUnder where

import qualified Data.Map as M
import qualified Data.List as List
import ProbFSTA

------------------------------------------------------------------------------------------------------------------------------------
type SoftCounts = M.Map HiddenEvent Double
--[(HiddenEvent, Double)]

data HiddenEvent = HStart State | HStep State NodeLabel [State] deriving (Show,Eq,Ord)


sumCounts :: [SoftCounts] -> SoftCounts
sumCounts xs = 
	let zeroCounts = M.fromList [] in --empty map
    let addCounts m1 m2 = M.unionWith (+) m1 m2 in 
    foldl addCounts zeroCounts xs

--unionWith: takes two maps and do the union based on keys; for two keys that are the same, do a combining function (here is simply add things up)
             --for two HiddenEevnts that are the same, adds their probablities up

--foldl takes the zeroCounts and the first elment of xs and applies addCounts to them.
        --Then, it applies addCounts to the result and the next item in the list. 

------------------------------utility funcs
normalize :: M.Map a Double -> M.Map a Double
normalize m =
    let total = sum (M.elems m) in
    M.map (/total) m
    


--M.elems returns all values of the map in the ascending order of their keys
--So here, it returns probabilities summed together


----------------------------------------------------------------------------------------------------------------
---------------------------------------------------------
-- Observing a tree provides a collection of ``observed events''. 
-- For example, observing (Branching "S" [Branching "NP" [Leaf "I"], Branching "VP" [Leaf "eat"]]) amounts to observing 

--  - a starting event for (Branching "S" [Branching "NP" [Leaf "I"], Branching "VP" [Leaf "eat"]]

--  - a transition event for "Branching S [Tree]", after "" and before ([Branching "NP" [Leaf "I"], Branching "VP" [Leaf "eat"])

--  - a transition event for "Branching NP [Tree]", after "Branching S" and before "Leaf "I""
--  - a transition event for "Branching VP", after "Branching S" and before "Leaf "eat""

--  - a transition event for "Leaf "I" []", after "Branching NP" and before ""
--  - a transition event for "Leaf "eat" []", after "Branching VP" and before ""

-- The total number of such observed events in a tree (or corpus) 
-- will equal the total of the two kinds of soft counts that we calculate.

data ObservedEvent = Start Tree | Mid TreeCxt NodeLabel [Tree] deriving Show --questions on this

observedEvents :: Tree -> [ObservedEvent]
observedEvents tree = [Start tree] ++ [Mid (getCxt tree i) (getLabel tree i) (getSubtree tree i)  | i <- getAdsList tree]

----------------------------------E-step
expectationsFromObs :: ProbFSTA -> ObservedEvent -> SoftCounts
expectationsFromObs m e =
    let (initprob, trprob, states) = m in
    case e of
    Start tree ->
        let likelihoods = M.fromList [(HStart q,  (startProb m q * underValue m tree q)) | q <- states] in
        normalize likelihoods 
    Mid before str after ->
        let k = length after in 
        if k == 0 
        	then let likelihoods = M.fromList [(HStep q1 str q2, overValue m before q1 * trProb m (q1,q2) str * product(map (\(sbt, st) -> underValue m sbt st) (zip after q2)))  | q1 <- states, q2 <- [[]]] in 
        	normalize likelihoods 
        	else let likelihoods = M.fromList [(HStep q1 str q2, overValue m before q1 * trProb m (q1,q2) str * product(map (\(sbt, st) -> underValue m sbt st) (zip after q2))) | q1 <- states, q2 <- possList k states] in 
        	normalize likelihoods

expectationsFromObsNoOrder::ProbFSTA -> ObservedEvent -> SoftCounts
expectationsFromObsNoOrder m e = 
    let (initprob, trprob, states) = m in 
    case e of 
        Start tree ->let likelihoods = M.fromList [(HStart q,  (startProb m q * underValueNoOrder m tree q)) | q <- states] in
                     normalize likelihoods 
        Mid before str after -> let k = length after in 
                                if k == 0 
                                    then let likelihoods = M.fromList [(HStep q1 str q2, overValueNoOrder m before q1 * trProb m (q1,q2) str * product(map (\(sbt, st) -> underValue m sbt st) (zip after q2)))  | q1 <- states, q2 <- [[]]] in 
                                    normalize likelihoods 
                                    else let likelihoods = M.fromList [(HStep q1 str q2, overValueNoOrder m before q1 * trProb m (q1,q2) str * sum (map (\stateSeq -> product(map (\(sbt, st) -> underValueNoOrder m sbt st) (zip after stateSeq))) (filterThrough states q2)))| q1 <- states, q2 <- possListNoOrder k states] in 
                                    normalize likelihoods



-- This just tallies up all the expected/soft counts across all observed events 
-- from all string in the corpus.
expectationsFromCorpus :: ProbFSTA -> [Tree] -> SoftCounts
expectationsFromCorpus fsta trees =
    sumCounts [expectationsFromObs fsta o| s <- trees, o <- observedEvents s]

expectationsFromCorpusNoOrder::ProbFSTA -> [Tree] -> SoftCounts
expectationsFromCorpusNoOrder fsta trees =
    sumCounts [expectationsFromObsNoOrder fsta o| s <- trees, o <- observedEvents s]
-------------------------------M-step
estimate_from_counts :: ([State]) -> SoftCounts -> ProbFSTA
estimate_from_counts (states) counts =
    let startDist = normalize (M.fromList [(q, c)| (HStart q, c) <- M.assocs counts]) in
    let stepDist q = normalize (M.fromList [((q, str,qlist), c)  | (HStep q1 str qlist, c) <- M.assocs counts, q1 == q]) in
    let newInitFn = M.toList startDist in
    let newTrFn =  concat(map (\st-> M.toList (stepDist st)) states) in
    (newInitFn, newTrFn, states)

--softCounts is a map storing (HiddenEvent, probability) pairs. 
--Map assocs: returns all key value pairs

--findWithDefault returns the value at key (second argument) or returns the default (first argument) when the key is not in the map
                  --So in this case, it will returns 0.0 or the key 


update :: ProbFSTA -> [Tree] -> ProbFSTA
update m trees =
    let (initprob, trprob, states) = m in
    let expected_counts = expectationsFromCorpus m trees in
    estimate_from_counts (states) expected_counts

updateNoOrder :: ProbFSTA -> [Tree] -> ProbFSTA
updateNoOrder m trees =
    let (initprob, trprob, states) = m in
    let expected_counts = expectationsFromCorpusNoOrder m trees in
    estimate_from_counts (states) expected_counts

likelihood :: ProbFSTA -> [Tree] -> Double
likelihood m trees = product (map (\elem -> treeprobViaUnder m elem) trees)

likelihoodNoOrder :: ProbFSTA -> [Tree] -> Double
likelihoodNoOrder m trees = product (map (\elem -> treeprobViaUnderNoOrder m elem) trees)

-- Same as the plain update function but reports new likelihood as well
update' :: ProbFSTA -> [Tree] -> (ProbFSTA, Double)
update' fsta trees =
    let new_fsta = update fsta trees in
    let new_likelihood = likelihood new_fsta trees in
    (new_fsta, new_likelihood)

updateN:: Int -> ProbFSTA -> [Tree] -> ProbFSTA
updateN 0 m trees = m 
updateN 1 m trees = update m trees
updateN n m trees = update (updateN (n-1) m trees) trees 

updateNNoOrder:: Int -> ProbFSTA -> [Tree] -> ProbFSTA
updateNNoOrder 0 m trees = m 
updateNNoOrder 1 m trees = updateNoOrder m trees
updateNNoOrder n m trees = updateNoOrder (updateNNoOrder (n-1) m trees) trees 

