#### aiming for this quarter
* M-step
* Debugging and make sure that the haskell implementation and the python implementation yield the same result

#### planning for next quarter
* Random generation of tree corpora
  * from the syntactic restriction (_TreeGen1::Restriction -> corpora_)  
  * from a PFSTA (_TreeGen2::PFSTA -> corpora_)  
 The goal of this approach is to make sure that taking this generated corpora, the EM learner can still output the (exact) grammar

* A version of EM that's insensitive to the ordering of the transition states _([2, 1] == [1, 2])_
* Given a larger corpora (still toy example), are we able to replicate what we find for haskell small corpora?
* Get parsing of CHILDES figured out
* Explore around of the CHILDES
