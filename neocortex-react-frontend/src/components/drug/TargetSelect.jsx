import React from 'react';
import { FormControl, FormHelperText, InputLabel, MenuItem, Select } from '@mui/material';
import { TARGET_CATEGORIES, TARGET_DATABASE } from '../../constants/targets';

function TargetSelect({ value, onChange, label = 'Molecular target', size, showDescription = true }) {
  return (
    <FormControl fullWidth size={size}>
      <InputLabel>{label}</InputLabel>
      <Select value={value} onChange={(event) => onChange(event.target.value)} label={label}>
        {Object.entries(TARGET_CATEGORIES).map(([category, keys]) => [
          <MenuItem key={category} disabled>
            <em>{category}</em>
          </MenuItem>,
          ...keys.map((key) => (
            <MenuItem key={key} value={key} sx={{ pl: 4 }}>
              {TARGET_DATABASE[key].label}
            </MenuItem>
          )),
        ])}
      </Select>
      {showDescription && <FormHelperText>{TARGET_DATABASE[value]?.description}</FormHelperText>}
    </FormControl>
  );
}

export default TargetSelect;
