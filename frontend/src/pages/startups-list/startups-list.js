import { useEffect, useState } from 'react';
import axiosInstance from '../../api/axios-instance';
import StartupCard from '../../components/startup-card/startup-card';
import { ENDPOINTS } from '../../api/config';
import './startups-list.css';

const StartupsPage = () => {
  const [startups, setStartups] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const imageUrl = 'https://www.wsetglobal.com/media/14791/1608x900-wine-colours.png';

  useEffect(() => {
    const fetchStartups = async () => {
      try {
        const response = await axiosInstance.get(ENDPOINTS.STARTUP_LIST);
        setStartups(response.data); // Assuming response contains an array of startups
        setLoading(false);
      } catch (err) {
        console.error('Error fetching startups:', err);
        setError('Failed to load startups');
        setLoading(false);
      }
    };

    fetchStartups();
  }, []);

  if (loading) return <div>Loading startups...</div>;
  if (error) return <div>{error}</div>;

  return (
    <div className="startups-page">
      <h1 className="page-title">Startups</h1>
      <div className="startups-grid">
        {startups.map((startup) => (
          <StartupCard
            key={startup.id}
            image={imageUrl}
            company_name={startup.company_name}
            city={startup.city}
            country={startup.country}
            industry={startup.industry}
          />
        ))}
      </div>
    </div>
  );
};

export default StartupsPage;