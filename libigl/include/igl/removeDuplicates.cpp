#include "removeDuplicates.h"
#include <vector>

//template <typename T, typename S>
//IGL_INLINE void igl::removeDuplicates(
//                                 const Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic> &V,
//                                 const Eigen::Matrix<S, Eigen::Dynamic, Eigen::Dynamic> &F,
//                                 Eigen::Matrix<T, Eigen::Dynamic, Eigen::Dynamic> &NV,
//                                 Eigen::Matrix<S, Eigen::Dynamic, Eigen::Dynamic> &NF,
//                                 Eigen::Matrix<S, Eigen::Dynamic, 1> &I,
//                                 const double epsilon)
template <typename DerivedV, typename DerivedF>
IGL_INLINE void igl::removeDuplicates(
  const Eigen::PlainObjectBase<DerivedV> &V,
  const Eigen::PlainObjectBase<DerivedF> &F,
  Eigen::PlainObjectBase<DerivedV> &NV,
  Eigen::PlainObjectBase<DerivedF> &NF,
  Eigen::Matrix<typename DerivedF::Scalar, Eigen::Dynamic, 1> &I,
  const double epsilon)
{
  using namespace std;
  //// build collapse map
  int n = V.rows();
  
  I = Eigen::Matrix<typename DerivedF::Scalar, Eigen::Dynamic, 1>(n);
  I[0] = 0;
  
  bool *VISITED = new bool[n];
  for (int i =0; i <n; ++i)
    VISITED[i] = false;
  
  NV.resize(n,V.cols());
  int count = 0;
  Eigen::VectorXd d(n);
  for (int i =0; i <n; ++i)
  {
    if(!VISITED[i])
    {
      NV.row(count) = V.row(i);
      I[i] = count;
      VISITED[i] = true;
      for (int j = i+1; j <n; ++j)
      {
        if((V.row(j) - V.row(i)).norm() < epsilon)
        {
          VISITED[j] = true;
          I[j] = count;
        }
      }
      count ++;
    }
  }
  
  NV.conservativeResize  (  count , Eigen::NoChange );

  count = 0;
  std::vector<typename DerivedF::Scalar> face;
  NF.resize(F.rows(),F.cols());
  for (int i =0; i <F.rows(); ++i)
  {
    face.clear();
    for (int j = 0; j< F.cols(); ++j)
      if(std::find(face.begin(), face.end(), I[F(i,j)]) == face.end())
         face.push_back(I[F(i,j)]);
    if (face.size() == size_t(F.cols()))
    {
      for (unsigned j = 0; j< F.cols(); ++j)
        NF(count,j) = face[j];
      count ++;
    }
  }
  NF.conservativeResize  (  count , Eigen::NoChange );
  
  delete [] VISITED;
}

#ifndef IGL_HEADER_ONLY
// Explicit template specialization
template void igl::removeDuplicates<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> >&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> >&, Eigen::Matrix<Eigen::Matrix<int, -1, -1, 0, -1, -1>::Scalar, -1, 1, 0, -1, 1>&, double);
#endif