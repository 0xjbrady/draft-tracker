import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Box,
  Breadcrumbs,
  Container,
  IconButton,
  Link,
  Toolbar,
  Typography,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import HomeIcon from '@mui/icons-material/Home';
import FormatListNumberedIcon from '@mui/icons-material/FormatListNumbered';

interface LayoutProps {
  children: React.ReactNode;
}

const navItems = [
  { path: '/', label: 'Draft Board', icon: <HomeIcon /> },
  { path: '/rankings', label: 'Rankings', icon: <FormatListNumberedIcon /> },
];

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const location = useLocation();

  const getBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [
      {
        path: '/',
        label: 'Home',
      },
    ];

    if (pathSegments.length > 0) {
      if (pathSegments[0] === 'rankings') {
        breadcrumbs.push({
          path: '/rankings',
          label: 'Rankings',
        });
      } else if (pathSegments[0] === 'player' && pathSegments[1]) {
        breadcrumbs.push({
          path: '/rankings',
          label: 'Rankings',
        });
        breadcrumbs.push({
          path: `/player/${pathSegments[1]}`,
          label: decodeURIComponent(pathSegments[1]),
        });
      }
    }

    return breadcrumbs;
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NFL Draft Odds Tracker
          </Typography>
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 2 }}>
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  component={RouterLink}
                  to={item.path}
                  color="inherit"
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    textDecoration: 'none',
                    '&:hover': { opacity: 0.8 },
                  }}
                >
                  {item.icon}
                  <Typography>{item.label}</Typography>
                </Link>
              ))}
            </Box>
          )}
          {isMobile && (
            <Box sx={{ display: 'flex' }}>
              {navItems.map((item) => (
                <IconButton
                  key={item.path}
                  component={RouterLink}
                  to={item.path}
                  color="inherit"
                  size="large"
                >
                  {item.icon}
                </IconButton>
              ))}
            </Box>
          )}
        </Toolbar>
      </AppBar>

      <Container maxWidth="lg" sx={{ flex: 1, py: 4 }}>
        <Breadcrumbs sx={{ mb: 3 }}>
          {getBreadcrumbs().map((crumb, index, array) => {
            const isLast = index === array.length - 1;
            return isLast ? (
              <Typography key={crumb.path} color="text.primary">
                {crumb.label}
              </Typography>
            ) : (
              <Link
                key={crumb.path}
                component={RouterLink}
                to={crumb.path}
                color="inherit"
                sx={{ textDecoration: 'none', '&:hover': { textDecoration: 'underline' } }}
              >
                {crumb.label}
              </Link>
            );
          })}
        </Breadcrumbs>
        {children}
      </Container>

      <Box
        component="footer"
        sx={{
          py: 3,
          px: 2,
          mt: 'auto',
          backgroundColor: (theme) =>
            theme.palette.mode === 'light'
              ? theme.palette.grey[200]
              : theme.palette.grey[800],
        }}
      >
        <Container maxWidth="lg">
          <Typography variant="body2" color="text.secondary" align="center">
            NFL Draft Odds Tracker • {new Date().getFullYear()}
          </Typography>
        </Container>
      </Box>
    </Box>
  );
};

export default Layout; 