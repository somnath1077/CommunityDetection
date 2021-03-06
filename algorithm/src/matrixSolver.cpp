#include <iostream>
#include <Eigen/Sparse>
#include <Eigen/Dense>
#include <vector>
#include "graph.hpp"
//#include "seedNode.hpp"

// declares a column-major sparse matrix type of double
typedef Eigen::SparseMatrix<double> SMatD;
// A triplet is a simple object representing a non-zero entry as 
// the triplet: row index, column index, value.
typedef Eigen::Triplet<double> TripletD; 

using namespace std;
using namespace Eigen;

void solveMatrices(Graph &g, SMatD &D, SMatD &A, SMatD &R) {

    auto D_A = D - A;

    // perform a Cholesky factorization of (D-A)
    SimplicialCholesky<SMatD> chol(D_A);

    const int numberOfCommunities = g.numCommunities();
    const int numberOfSeedNodes = g.numSeed();
    const int numberOfNodes = g.numVertices();
    const int numberOfNonSeedNodes = numberOfNodes - numberOfSeedNodes;

    //for every community
    for (int l = 0; l < numberOfCommunities; ++l) {

        // fill vector
        VectorXd b = VectorXd::Zero(numberOfNonSeedNodes);
        for (int s = 0; s < numberOfSeedNodes; ++s) {
            double affinity = g.getAffinities(g.getVertexId(s)).at(l);
            b += affinity * R.col(s);
        }

        // use the factorization to solve for the given right hand side
        VectorXd x = chol.solve(b);

        //write the affinities for community l
        for(int i=0; i<numberOfNodes;++i){
            if(!g.isSeed(i)){
                g.getAffinities(i).push_back(x(g.getMatrixIndex(i)));
            } 
        }
    }

    //for (int i = 0; i < numberOfNodes ; i++) {
        //double tmp = 0;
        //for(int j = 0; j < numberOfCommunities; j++) {
            //tmp += g.getAffinities(i).at(j);
        //}
        //cout << tmp << " ";
    //}
}
