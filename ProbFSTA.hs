{-# LANGUAGE TypeSynonymInstances, FlexibleInstances #-}
module ProbFSTA where


import qualified Data.Map as M
import qualified Data.List as List
import Control.Applicative
tbl ! key = --trace ("Looking up key " ++ show key ++ "\n")
            (case M.lookup key tbl of {Just x -> x; Nothing -> error ("Couldn't find key " ++ show key)})

 


----------------------------------------------
-----------------------------PFSTA declaration
----------------------------------------------
type State = Int
type NodeLabel = String
type ProbFSTA = ([(State,Double)],                  -- start distribution
                [((State, NodeLabel, [State]), Double)], --transition probabilities: making sure it's locally normalized (the probabilities ending )
                [State])                       -- all states

data Tree = Leaf NodeLabel | Branching NodeLabel [Tree] deriving (Show, Eq, Ord)
type Address = [Int]  -- get the address in the tree of the node
                       --[]: root;  00: leftmost daughter; 0n

---context a = Root |Nonroot mother Tree_context_of_its_mother  left_sisters right_sisters
data TreeCxt = Root | Nonroot NodeLabel TreeCxt [Tree] [Tree] deriving (Show, Eq, Ord)


----------------------------------------------
-----------------------------Grammar utilities
----------------------------------------------
probLookup :: (Eq a) => [(a,Double)] -> a -> Double
probLookup []           key = 0.0
probLookup ((x,y):rest) key = if key == x then y else probLookup rest key

allStates :: ProbFSTA -> [State]
allStates (starting,transitions, states) = states

startProb :: ProbFSTA -> State -> Double
startProb (starting,transitions, states) st = probLookup starting st

trProb :: ProbFSTA -> (State, [State]) -> String -> Double
trProb (starting, transitions,states) (st1, stl) str = probLookup transitions (st1, str, stl)


----------------------------------------------
--------------------------------Tree utilities
----------------------------------------------
--input: a set of trees, nth index
--goal: get the nth tree of the list of trees; the list starts at 0
nthsubt:: [Tree] -> Int -> Tree
nthsubt [] 0 = error"No subtrees"
nthsubt tst 0 = head tst
nthsubt tst num = nthsubt (tail tst) (num-1) 

--Given a tree T and an interested address, output the node label at such address in T
getLabel:: Tree -> Address -> NodeLabel
getLabel (Leaf str) ads = if ads == [] then str else undefined
getLabel (Branching str subts) [] = str
getLabel (Branching str subts) ads = getLabel (nthsubt subts (head ads)) (tail ads)

--Given a tree T and an interested address, output subtrees of the node at such address in T
getSubtree:: Tree -> Address -> [Tree]
getSubtree (Leaf str) ads = if ads == [] then [] else undefined
getSubtree (Branching str subts) [] = subts
getSubtree (Branching str subts) ads = getSubtree (nthsubt subts (head ads)) (tail ads)

--Given a tree T and an interested address, output the left sister of the node at such address in T
getLeftSis:: Tree -> Address -> [Tree]
getLeftSis (Leaf str) ads = []
getLeftSis tr [] = []
getLeftSis tr [one] = take (one) (getSubtree tr []) 
getLeftSis (Branching str subts) ads = getLeftSis (nthsubt subts (head ads))  (tail ads)

--Given a tree T and an interested address, output the right sister of the node at such address in T
getRightSis::Tree -> Address -> [Tree]
getRightSis (Leaf str) ads = []
getRightSis tr [] = []
getRightSis tr [one] = drop (one+1) (getSubtree tr []) 
getRightSis (Branching str subts) ads = getRightSis (nthsubt subts (head ads))  (tail ads)

--Given a tree T and an interested address, output the context of the node at such address in T
getCxt:: Tree -> Address -> TreeCxt
getCxt (Leaf str) ads = if ads == [] then Root else undefined
getCxt (Branching str subts) [] = Root
getCxt btr ads = Nonroot (getLabel btr (init ads)) (getCxt btr (init ads)) (getLeftSis btr ads) (getRightSis btr ads)

--Given a tree T, output a list of addresses of all its node
--Depth-first, from left to right
getAdsList::Tree -> [Address]
getAdsList (Leaf str) = [[]]
getAdsList (Branching ndl subtrees) =  let treeNumPair = zip subtrees [0..length subtrees-1]
    in  [[]]++concat (map (\elem -> (map (\ads -> [snd elem]++ads) (getAdsList (fst elem)))) (treeNumPair)) 


---------------------------------------------
---------------over and under value utilities
---------------------------------------------
possList:: Int -> [State] -> [[State]]
possList 0 stset = []
possList 1 stset = map (\elem -> [elem]) (stset) 
possList n stset = concat (map (\elem -> map (\x -> elem++[x]) (stset)) (possList (n-1) stset))

sameParameter::[State] -> [State] -> Bool
sameParameter [] [] = True
sameParameter [] (x:xs) = False
sameParameter (x:xs) p = if elem x p then sameParameter xs (List.delete x p) else False

removeReduplicates::Eq a => [a] -> [a]
removeReduplicates [] = []
removeReduplicates (x:xs) = if elem x xs then removeReduplicates xs else x:(removeReduplicates xs)

possListNoOrder::Int -> [State]->[[State]]
possListNoOrder n stset = let candidate = possList n stset in 
                          let samePs q = filter (sameParameter q) candidate in
                          let finalCand =  (map (\x -> samePs x) candidate) in
                          let removedCopies = removeReduplicates finalCand in
                          (concat (map (\x -> [head x]) removedCopies))

filterThrough::[State] -> [State] -> [[State]]
filterThrough stset para = filter (sameParameter para) (possList (length para) stset)


zipthree:: [[State]] -> [[State]] -> [State] -> [([State],[State], State)]
zipthree [] [] [] = undefined
zipthree [] [] st = [ ([], [],y) | y<-st ]
zipthree [] rseq st = [ ([], x,y) | x<-rseq, y<-st ]
zipthree lseq [] st = [ (x,[],y) | x<-lseq, y<-st ]
zipthree lseq rseq st = [(x, y, z)| x<-lseq, y<-rseq, z<-st]


treeChunk:: Tree -> [Tree]
treeChunk (Leaf str) = [Leaf str]
treeChunk (Branching ndl subtrees) = concat (map (\x-> treeChunk x) subtrees) ++ [Branching ndl subtrees]

cxtChunk::TreeCxt -> [TreeCxt]
cxtChunk cxt = case cxt of 
	                Root -> [Root]
	                Nonroot nlb momCxt lsubt rsubt -> cxtChunk momCxt ++ [cxt]
---------------------------------------------
--------------recursive over and under values
---------------------------------------------


probUnder :: ProbFSTA -> Tree -> State -> Double
probUnder pfsa (Leaf ndl) st = trProb pfsa (st, []) ndl  -- base case with only leaf node so lookup in pfsa probablity of ending in state st with node label ndl
probUnder pfsa (Branching ndl subtrees) st = let k = length subtrees in
         sum(map (\stateSeq -> (product(map (\(sbt, state) -> (probUnder pfsa sbt state)) (zip subtrees stateSeq)))* trProb pfsa (st, stateSeq) ndl) (possList k (allStates pfsa)))



probOver:: ProbFSTA -> TreeCxt -> State -> Double
probOver pfsa Root st = startProb pfsa st
probOver pfsa (Nonroot str cxt lsubt rsubt) st = let stateList = allStates pfsa in
	let kl = length lsubt in 
            let kr = length rsubt in 
            sum(map (\(lstateSeq, rstateSeq, momState) -> (probOver pfsa cxt momState)*
            	                                           product(map (\(sbt, state) -> (probUnder pfsa sbt state)) (zip lsubt lstateSeq)) * 
            	                                           product(map (\(rsbt, rstate) -> (probUnder pfsa rsbt rstate)) (zip rsubt rstateSeq)) *
            	                                           trProb pfsa (momState, concat [lstateSeq, [st], rstateSeq]) str)
                (zipthree (possList kl stateList) (possList kr stateList) (stateList)))


---------------------------------------------
--fast over and under values through hashmaps
---------------------------------------------


underTable :: ProbFSTA -> Tree -> M.Map (Tree,State) Double
underTable pfsta tree =
     let (start, trans, state) = pfsta in
     let underValue tbl tr st =
             case tr of
             Leaf ndl -> trProb pfsta (st, []) ndl
             Branching ndl subtrees -> sum(map (\stateSeq -> (product(map (\(sbt, stateVar) -> (tbl ! (sbt, stateVar))) (zip subtrees stateSeq)))* trProb pfsta (st, stateSeq) ndl) (possList (length subtrees) (allStates pfsta)))
     in
     let chunks = treeChunk tree in
     let updateTable tbl (chunk,n) = M.insert (chunk,n) (underValue tbl chunk n) tbl in
     foldl updateTable M.empty [(chunk,n) | chunk <- chunks, n <- allStates pfsta]

underValue :: ProbFSTA -> Tree -> State -> Double
underValue pfsta tree state = (underTable pfsta tree) ! (tree,state)



underTableNoOrder :: ProbFSTA -> Tree -> M.Map (Tree,State) Double
underTableNoOrder pfsta tree =
     let (start, trans, state) = pfsta in
     let underValueNoOrder tbl tr st =
             case tr of
             Leaf ndl -> trProb pfsta (st, []) ndl
             Branching ndl subtrees -> sum(map (\statePara -> sum (map (\stateSeq -> product(map (\(sbt, stateVar) -> (tbl ! (sbt, stateVar))) (zip subtrees stateSeq))) (filterThrough state statePara))* trProb pfsta (st, statePara) ndl) (possListNoOrder (length subtrees) (allStates pfsta)))
     in
     let chunks = treeChunk tree in
     let updateTable tbl (chunk,n) = M.insert (chunk,n) (underValueNoOrder tbl chunk n) tbl in
     foldl updateTable M.empty [(chunk,n) | chunk <- chunks, n <- allStates pfsta]

underValueNoOrder :: ProbFSTA -> Tree -> State -> Double
underValueNoOrder pfsta tree state = (underTableNoOrder pfsta tree) ! (tree,state)

listBreak::[a] -> Int -> Int -> ([a], [a], [a])
listBreak st k1 k2 = if k1 == 0 then ([], [head st], tail st) else ([st !! i|i <- [0..k1-1]], [st !! k1], [st!! i | i<- [(k1+1)..length st -1]])

overTableNoOrder :: ProbFSTA -> TreeCxt -> M.Map (TreeCxt,State) Double
overTableNoOrder pfsta cxt=
    let (start, trans, state) = pfsta in
    let overValueNoOrder tbl tct st =
            case tct of
            Root -> startProb pfsta st
            Nonroot nlb momCxt lsubt rsubt -> let stateList = allStates pfsta in
                                              let kl = length lsubt in 
                                              let kr = length rsubt in
                                              sum (map (\momState -> (tbl ! (momCxt, momState))* 
                                                                     sum(map (\(statePara) -> sum(map (\stateSeq -> (let (lstateSeq, currentState, rstateSeq) = listBreak stateSeq kl kr in 
                                                                                                                     if currentState == [st] 
                                                                                                                        then (product(map (\(sbt, state) -> (underValueNoOrder pfsta sbt state)) (zip lsubt lstateSeq))) * 
                                                                                                                             (product(map (\(rsbt, rstate) -> (underValueNoOrder pfsta rsbt rstate)) (zip rsubt rstateSeq)))
                                                                                                                        else 0.0)) 
                                                                                              (filterThrough stateList statePara)) *trProb pfsta (momState, statePara) nlb) 
                                                                     (possListNoOrder (kl + kr +1) stateList)))
                                              stateList)                                          
    in
    let chunks = cxtChunk cxt in
    let updateTable tbl (chunk,n) = M.insert (chunk,n) (overValueNoOrder tbl chunk n) tbl in
    foldl updateTable M.empty [(chunk,n) | chunk <- chunks, n <- allStates pfsta]


overValueNoOrder :: ProbFSTA -> TreeCxt -> State -> Double
overValueNoOrder pfsta cxt state = (overTableNoOrder pfsta cxt) ! (cxt,state)



overTable :: ProbFSTA -> TreeCxt -> M.Map (TreeCxt,State) Double
overTable pfsta cxt=
    let (start, trans, state) = pfsta in
    let overValue tbl tct st =
            case tct of
            Root -> startProb pfsta st
            Nonroot nlb momCxt lsubt rsubt -> let stateList = allStates pfsta in
                                              let kl = length lsubt in 
                                              let kr = length rsubt in
                                              sum(map (\(lstateSeq, rstateSeq, momState) -> (tbl ! (momCxt, momState))*
                                                           (product(map (\(sbt, state) -> (underValue pfsta sbt state)) (zip lsubt lstateSeq))) * 
                                                           (product(map (\(rsbt, rstate) -> (underValue pfsta rsbt rstate)) (zip rsubt rstateSeq))) *
                                                           trProb pfsta (momState, concat [lstateSeq, [st], rstateSeq]) nlb)
                                              (zipthree (possList kl stateList) (possList kr stateList) (stateList))) 
    in
    let chunks = cxtChunk cxt in
    let updateTable tbl (chunk,n) = M.insert (chunk,n) (overValue tbl chunk n) tbl in
    foldl updateTable M.empty [(chunk,n) | chunk <- chunks, n <- allStates pfsta]


overValue :: ProbFSTA -> TreeCxt -> State -> Double
overValue pfsta cxt state = (overTable pfsta cxt) ! (cxt,state)

---------------------------------------------
---------------Tree probabilities------------
---------------------------------------------

treeprobViaUnder :: ProbFSTA -> Tree -> Double
treeprobViaUnder m tree = sum [startProb m q * underValue m tree q | q <- allStates m]

treeprobViaOver :: ProbFSTA -> Tree -> Double
treeprobViaOver m tree = sum [startProb m q * overValue m (getCxt tree []) q | q <- allStates m]

treeprobViaUnderNoOrder :: ProbFSTA -> Tree -> Double
treeprobViaUnderNoOrder m tree = sum [startProb m q * underValueNoOrder m tree q | q <- allStates m]

treeprobViaOverNoOrder :: ProbFSTA -> Tree -> Double
treeprobViaOverNoOrder m tree = sum [startProb m q * overValueNoOrder m (getCxt tree []) q | q <- allStates m]


---------------------------------------------
---------------For showing PFSTA------------
---------------------------------------------

{-nodes::[((State, NodeLabel, [State]), Double)] -> [NodeLabel]
nodes trans = case trans of 
	            [] -> []
	            x:list -> let ((_, ndl, _), _) = x in [ndl] ++ nodes list


sigma:: ProbFSTA ->[NodeLabel]
sigma (_, trans, _) = nodes trans


stateSeq:: ProbFSTA ->[[State]]
stateSeq (_, trans, _) = let stateSeqG tt = case tt of 
	                                         [] -> []
	                                         x:list -> let ((_,_, seq), _) = x in [seq] ++ stateSeqG list
	                  in stateSeqG trans
-}

{-showProbFSTA :: ProbFSTA -> String
showPCFG pfsta = let (start, trans, state) = pfsta in
    let stStrs = ["States = "]++[show n | n <- state] in
    let iStrs = ["I(" ++ show n ++ ") = " ++ show (startProb pfsta n) | n <- state, startProb pfsta n /= 0] in
    --let fStrs = ["R(" ++ List.intercalate "," [show n, show x, show stseq] ++ ") = " ++ show (trProb pfsta (n, stseq) x) | n <- state, x <- sigma pfsta, stseq <-stateSeq pfsta, trProb pfsta (n, stseq) x /= 0] in                                                                                                r (NTRule n (ld,rd)) /= 0] in
    unlines (stStrs ++ iStrs)

instance {-# OVERLAPPING #-} Show ProbFSTA where
    show = showProbFSTA-}


---------------------------------------------
---------------Test cases------------
---------------------------------------------
--with one states, more than one branches
pfsta1 :: ProbFSTA
pfsta1 = ([(1,1.0)],
          [((1, "with", []), 1.0), ((1, "saw", []), 1.0), ((1, "dogs", []), 1.0), ((1, "telescopes", []), 1.0), ((1, "saw",[]), 1.0), ((1, "cats", []), 1.0), ((1, "hamsters", []), 1.0), --leaves
           ((1, "P", [1]), 1.0), ((1, "V", [1]), 1.0), ((1, "NP", [1]), 1.0), ((1, "S", [1, 1]), 1.0), ((1, "PP", [1, 1]), 1.0), ((1, "VP", [1, 1]), 1.0), ((1, "NP", [1, 1]), 1.0)], 
           [1])

--with more than one states, one branches
pfsta2::ProbFSTA
pfsta2 = ([(1, 1.0)], [((1, "V", [1]), 0.18), ((1,"C",[2]), 0.5), ((1,"V",[3]), 0.12), ((2,"V",[3]), 0.4), ((2,"V",[1]), 0.6),  ((3,"C",[1]), 1.0), ((1, "\n", []), 0.2)], [1, 2,3])

--with more than one states, more than one branches
pfsta3 :: ProbFSTA
pfsta3 = ([(1,0.2), (2, 0.8)],
            [((2, "with", [0]), 0.1), ((2, "saw", []), 0.2), ((2, "dogs", []), 0.2), ((2, "telescopes", []), 0.1), ((2, "chase",[]), 0.2), ((2, "cats", []), 0.1), ((2, "hamsters", []), 0.1), --leaves
              ((1, "P", [2]), 0.1), ((1, "V", [2]), 0.1), ((1, "V", [1,2]), 0.1) , ((1, "N", [2]), 0.1), ((1, "S", [1, 1]), 0.1), ((1, "PP", [1, 2]), 0.1), ((1, "VP", [1]), 0.03), ((1, "PP", [1, 1]), 0.07), ((1, "NP", [1, 1]), 0.1), ((1, "telescopes", []), 0.2)], 
             [1, 2])


tr1:: Tree
tr1= Branching "S" [Branching "NP" [Leaf "John"], Branching "VP" [Branching "VP" [Branching "V" [Leaf "saw"], Branching "NP" [Leaf "Mary"]], Branching "PP" [Branching "P" [Leaf "with"], Branching "NP" [Leaf "telescopes"]]]]


tr2::Tree
tr2 = Leaf "with"

tr3::Tree
tr3 = Branching "P" [tr2]

tr4::Tree
tr4 = Branching "PP" [tr3, Leaf "telescopes"]

tr5::Tree
tr5= Branching "0" [Branching "1" [Leaf "3"], Branching "2" [Leaf "4"]]

 
--- probOver pfsta3 (getCxt tr4 [1]) 2
--- 1.0000000000000002e-3
