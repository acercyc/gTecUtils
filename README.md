# gTecUtils
* Import g.tec HDf5 file
* Convert to MNE RawArray data type

```python
import gTecUtils as gu 

dataset = gu.gTecDataset("Z:\RecordSession_2021.08.27_17.36.03.hdf5")
mne_RawArray = dataset.toMNE()

```
2021/09/07 18:53