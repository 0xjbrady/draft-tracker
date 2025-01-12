import React from 'react';
import { Alert, AlertTitle, Button, Box } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

interface ErrorAlertProps {
  error: Error | string;
  onRetry?: () => void;
  severity?: 'error' | 'warning';
}

export const ErrorAlert: React.FC<ErrorAlertProps> = ({
  error,
  onRetry,
  severity = 'error'
}) => {
  const errorMessage = error instanceof Error ? error.message : error;

  return (
    <Box sx={{ my: 2 }}>
      <Alert
        severity={severity}
        action={
          onRetry && (
            <Button
              color="inherit"
              size="small"
              onClick={onRetry}
              startIcon={<RefreshIcon />}
            >
              Retry
            </Button>
          )
        }
      >
        <AlertTitle>
          {severity === 'error' ? 'Error' : 'Warning'}
        </AlertTitle>
        {errorMessage}
      </Alert>
    </Box>
  );
};

export default ErrorAlert; 