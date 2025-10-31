import { Request, Response, NextFunction } from 'express';

export const errorHandler = (err: any, req: Request, res: Response, next: NextFunction) => {
  console.error(err.stack);

  if (err.name === 'UnauthorizedError') {
    return res.status(401).json({
      error: 'Unauthorized access',
      message: 'Please provide valid authentication credentials'
    });
  }

  if (err.name === 'ValidationError') {
    return res.status(400).json({
      error: 'Validation Error',
      message: err.message
    });
  }

  return res.status(500).json({
    error: 'Internal Server Error',
    message: 'Something went wrong on the server'
  });
};
