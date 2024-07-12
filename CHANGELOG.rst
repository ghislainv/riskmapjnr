Changelog
=========

riskmapjnr 1.3.2
----------------

* Bug correction in ``benchmark/defrate_per_class.py`` due to missing classes when forecasting.
* See changes: https://github.com/ghislainv/riskmapjnr/compare/v1.3.1..v1.3.2

riskmapjnr 1.3.1
----------------

* Replace ``gdal.TermProgress`` with ``gdal.TermProgress_nocb``.
* See changes: https://github.com/ghislainv/riskmapjnr/compare/v1.3...v1.3.1

riskmapjnr 1.3
--------------

* Adding functions for the benchmark model.
* Update progress bar to mimic gdal outputs.
* Bug corrections.
* See changes: https://github.com/ghislainv/riskmapjnr/compare/v1.2...v1.2.1

riskmapjnr 1.2.1
----------------

* Bug corrections.
* Set non-forest area as NoData in ``set_defor_cat_zero.py``.

* This version is used by the Qgis Deforisk plugin.

riskmapjnr 1.2
--------------

* Improving documentation.
* Bug corrections:

  - Make sure that ``fcc_file`` is projected to compute distances.
  - Let the user set Agg backend for matplotlib when DISPLAY is not found.
  - Close and join the pool execution in ``makemap()``.

* This version is running without issues in `SEPAL <https://sepal.io>`_.

riskmapjnr 1.1
--------------

* Removing unnecessary output files.

riskmapjnr 1.0
--------------

* First stable release.
* Parallel computation for ``makemap()``.
* Benchmark to estimate advantage of parallel computing.
* New tutorials on large jurisdictions (countries).
* Bug corrections:
  
  - Correction of the annual deforestation rate formula.
  - Correction of the validation step using maps at the start of the validation period.
  - Correction of the final risk map at the end of the validation period.
  
riskmapjnr 0.1
--------------

* First alpha release of the package. Must be thoroughly tested.
  
