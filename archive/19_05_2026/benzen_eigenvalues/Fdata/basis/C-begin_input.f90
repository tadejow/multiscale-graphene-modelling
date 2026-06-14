         module begin_input 
          use precision 
   
          integer, parameter :: ioption =  3
          integer, parameter :: nexcite = 0
          integer, parameter :: nssh = 3
   
          integer, parameter :: nznuc =  6
          integer, parameter :: nzval =  4
          integer, parameter :: nzval_ion =  0
   
          integer, dimension (nssh), parameter ::                           &
     &     lam = (/ 0, 1, 2/)
   
          real(kind=long), dimension (nssh), parameter ::                   &
     &     a0 = (/ 2.0000, 1.0000, 0.8000/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     rcutoff = (/ 4.000, 4.500, 5.400/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     rcut_ion = (/ 4.000, 4.500, 5.400/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     xocc = (/ 2.00, 2.00, 0.00/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     xocc_ion = (/ 0.00, 0.00, 0.00/)
   
          character(len=10), parameter :: atomname = 'Carbon    '
          character(len=8), parameter :: ppfile = '006.pp  '
          character(len=8), parameter :: ppionfile = '006++.pp'
   
          character(len=11), dimension (0:nssh), parameter ::               &
     &     filename_na = (/'006_540.na0',                                   &
     &                     '006_400.na1',                                   &
     &                     '006_450.na2',                                   &
     &                     '006_540.na3'/)
          character(len=12), dimension (nssh), parameter ::                 &
     &     filename_ena = (/'006_400.ena1',                                 &
     &                      '006_450.ena2',                                 &
     &                      '006_540.ena3'/)
          character(len=11), dimension (nssh), parameter ::                 &
     &     filename_wf = (/'006_400.wf1',                                   &
     &                     '006_450.wf2',                                   &
     &                     '006_540.wf3'/)
          character(len=12), dimension (nssh), parameter ::                 &
     &     filename_ewf = (/'006_400.ewf1',                                 &
     &                      '006_450.ewf2',                                 &
     &                      '006_540.ewf3'/)
          integer, parameter :: ioptim =  1
          real(kind=long), dimension (nssh), parameter ::                   &
     &     Vo = (/    0.0000,    0.0000,   100.0000/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     r0 = (/ 0.00, 0.00, 0.50/)
          real(kind=long), dimension (nssh), parameter ::                   &
     &     cmix = (/ 1.00, 1.00, 1.00/)
   
         end module 
