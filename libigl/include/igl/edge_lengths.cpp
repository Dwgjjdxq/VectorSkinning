// This file is part of libigl, a simple c++ geometry processing library.
// 
// Copyright (C) 2013 Alec Jacobson <alecjacobson@gmail.com>
// 
// This Source Code Form is subject to the terms of the Mozilla Public License 
// v. 2.0. If a copy of the MPL was not distributed with this file, You can 
// obtain one at http://mozilla.org/MPL/2.0/.
#include "edge_lengths.h"
#include <iostream>

template <typename DerivedV, typename DerivedF, typename DerivedL>
IGL_INLINE void igl::edge_lengths(
  const Eigen::PlainObjectBase<DerivedV>& V,
  const Eigen::PlainObjectBase<DerivedF>& F,
  Eigen::PlainObjectBase<DerivedL>& L)
{
  using namespace std;
  switch(F.cols())
  {
    case 3:
    {
      L.resize(F.rows(),3);
      // loop over faces
      for(int i = 0;i<F.rows();i++)
      {
        L(i,0) = sqrt((V.row(F(i,1))-V.row(F(i,2))).array().pow(2).sum());
        L(i,1) = sqrt((V.row(F(i,2))-V.row(F(i,0))).array().pow(2).sum());
        L(i,2) = sqrt((V.row(F(i,0))-V.row(F(i,1))).array().pow(2).sum());
      }
      break;
    }
    case 4:
    {
      const int m = F.rows();
      L.resize(m,6);
      // loop over faces
      for(int i = 0;i<m;i++)
      {
        L(i,0) = sqrt((V.row(F(i,3))-V.row(F(i,0))).array().pow(2).sum());
        L(i,1) = sqrt((V.row(F(i,3))-V.row(F(i,1))).array().pow(2).sum());
        L(i,2) = sqrt((V.row(F(i,3))-V.row(F(i,2))).array().pow(2).sum());
        L(i,3) = sqrt((V.row(F(i,1))-V.row(F(i,2))).array().pow(2).sum());
        L(i,4) = sqrt((V.row(F(i,2))-V.row(F(i,0))).array().pow(2).sum());
        L(i,5) = sqrt((V.row(F(i,0))-V.row(F(i,1))).array().pow(2).sum());
      }
      break;
    }
    default:
    {
      cerr<< "edge_lengths.h: Error: Simplex size ("<<F.cols()<<
        ") not supported"<<endl;
      assert(false);
    }
  }
}

#ifndef IGL_HEADER_ONLY
// Explicit template specialization
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<float, -1, 2, 0, -1, 2>, Eigen::Matrix<unsigned int, -1, -1, 1, -1, -1>, Eigen::Matrix<float, -1, 2, 0, -1, 2> >(Eigen::PlainObjectBase<Eigen::Matrix<float, -1, 2, 0, -1, 2> > const&, Eigen::PlainObjectBase<Eigen::Matrix<unsigned int, -1, -1, 1, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<float, -1, 2, 0, -1, 2> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<double, -1, 3, 0, -1, 3>, Eigen::Matrix<int, -1, 3, 0, -1, 3>, Eigen::Matrix<double, -1, 3, 0, -1, 3> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 3, 0, -1, 3> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, 3, 0, -1, 3> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 3, 0, -1, 3> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<double, -1, 2, 0, -1, 2>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<double, -1, 2, 0, -1, 2> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 2, 0, -1, 2> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 2, 0, -1, 2> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<double, -1, 2, 0, -1, 2>, Eigen::Matrix<int, -1, 3, 0, -1, 3>, Eigen::Matrix<double, -1, 2, 0, -1, 2> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 2, 0, -1, 2> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, 3, 0, -1, 3> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 2, 0, -1, 2> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<double, -1, 6, 0, -1, 6> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 6, 0, -1, 6> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<double, -1, 3, 0, -1, 3> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, 3, 0, -1, 3> >&);
// generated by autoexplicit.sh
template void igl::edge_lengths<Eigen::Matrix<float, -1, 3, 1, -1, 3>, Eigen::Matrix<unsigned int, -1, -1, 1, -1, -1>, Eigen::Matrix<float, -1, 3, 1, -1, 3> >(Eigen::PlainObjectBase<Eigen::Matrix<float, -1, 3, 1, -1, 3> > const&, Eigen::PlainObjectBase<Eigen::Matrix<unsigned int, -1, -1, 1, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<float, -1, 3, 1, -1, 3> >&);
template void igl::edge_lengths<Eigen::Matrix<double, -1, -1, 0, -1, -1>, Eigen::Matrix<int, -1, -1, 0, -1, -1>, Eigen::Matrix<double, -1, -1, 0, -1, -1> >(Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<int, -1, -1, 0, -1, -1> > const&, Eigen::PlainObjectBase<Eigen::Matrix<double, -1, -1, 0, -1, -1> >&);
#endif
